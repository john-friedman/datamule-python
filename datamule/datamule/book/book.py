from .eftsquery import EFTSQuery
from .xbrlretriever import XBRLRetriever
from secsgml import parse_sgml_submission_into_memory
from ..helper import load_package_dataset, identifier_to_cik
from datetime import datetime

def compare_value(value, logic, amount):
    """
    Compare a single value against a target amount using specified logic
    """
    comparisons = {
        ">": lambda x, y: x > y,
        "<": lambda x, y: x < y,
        "=": lambda x, y: x == y,
        "!=": lambda x, y: x != y,
        ">=": lambda x, y: x >= y,
        "<=": lambda x, y: x <= y
    }
    return comparisons[logic](float(value), float(amount))

def get_company_values(xbrl_data, cik, periods):
    """
    Get list of values for a company across all periods
    Returns list of values in chronological order
    """
    values = []
    for period in periods:
        # Construct the URL key that matches XBRLRetriever's output
        url = f"https://data.sec.gov/api/xbrl/frames/us-gaap/AccountsPayableCurrent/USD/{period}.json"
        
        # Find matching record for this company in this period
        # Note: data is nested under 'data' key and value is 'val'
        if url in xbrl_data and 'data' in xbrl_data[url]:
            matches = [item['val'] for item in xbrl_data[url]['data'] 
                      if item['cik'] == cik]
            values.append(float(matches[0]) if matches else None)
        else:
            values.append(None)
    return values

def check_trend(values, logic):
    """
    Check if values follow specified trend (increasing/decreasing)
    Handles missing values by returning False
    """
    # Remove None values
    values = [v for v in values if v is not None]
    
    # Need at least 2 values to check trend
    if len(values) < 2:
        return False
        
    if logic == "increasing":
        return all(values[i] < values[i+1] 
                  for i in range(len(values)-1))
    elif logic == "decreasing":
        return all(values[i] > values[i+1] 
                  for i in range(len(values)-1))
    return False

def check_within_range(values, pct):
    """
    Check if all values are within ±percentage range of the mean
    Handles missing values by excluding them
    """
    # Remove None values
    values = [v for v in values if v is not None]
    
    if not values:
        return False
        
    mean = sum(values) / len(values)
    lower_bound = mean * (1 - pct/100)
    upper_bound = mean * (1 + pct/100)
    
    return all(lower_bound <= v <= upper_bound for v in values)


class Book():
    def __init__(self, cik=None,ticker=None,sic=None,submission_type=None,document_type=None,filing_date=None):
        self.EFTSQuery = EFTSQuery()
        self.XBRLRetriever = XBRLRetriever()

        # cleaning
        if ticker is not None:
            cik = identifier_to_cik(ticker)
        else:
            cik = cik

        if cik is not None:
            if isinstance(cik, str):
                cik = [str(cik)]
            else:
                cik = [str(c) for c in cik]

        if sic is not None:
            if isinstance(sic, str):
                sic = [sic]
            else:
                sic = [s for s in sic]

        if submission_type is not None:
            if isinstance(submission_type, str):
                submission_type = [str(submission_type)]
            else:
                submission_type = [str(s) for s in submission_type]

        if document_type is not None:
            if isinstance(document_type, str):
                document_type = [str(document_type)]
            else:
                document_type = [str(d) for d in document_type]


        if filing_date is None:
            filing_date = ("2001-01-01", datetime.now().strftime('%Y-%m-%d'))

        if isinstance(filing_date, str):
            filing_date = (filing_date,filing_date)

        self.cik = cik
        self.ticker = ticker
        self.sic = sic
        self.submission_type = submission_type
        self.document_type = document_type
        self.filing_date = filing_date

        # accession numbers, document filenames, and associated ciks that match search text
        self.search_text_data = []
        # ciks that match sic code
        self.sic_matches = None
        # xbrl matches that match xbrl query
        self.xbrl_matches = []

    # need to make this so that each call filters it more
    def filter_text(self,text=None,callback=None):
        search_text_data = self.EFTSQuery.query_efts(cik=self.cik, submission_type=self.submission_type,
                                             filing_date=self.filing_date, search_text=text)
        
        if callback is not None:
            callback(search_text_data)

        self.search_text_data.append((len(self.search_text_data),search_text_data))

    def filter_sic(self,sic=None):
        sics = load_package_dataset('company_metadata')
        sic_matches = [item['cik'] for item in sics if str(item['sic']) in sic]
        # cik codes
        self.sic_matches = (sic_matches)

    def filter_xbrl(self, taxonomy, concept, unit, periods, logic, amount=None, callback=None):

        if logic in ['>', '<', '=', '!=', '>=', '<='] and amount is None:
            raise ValueError("Amount must be provided for comparison logic")

        params = [{'taxonomy':taxonomy, 'concept':concept, 'unit':unit, 'period':period} for period in periods]
        xbrl_data = self.XBRLRetriever.get_xbrl_frames(params)

        if callback is not None:
            callback(xbrl_data)

        # Last period is where we get matching acc_nos from
        last_period = periods[-1]
        xbrl_matches = []

        # For each company in the last period
        for item in xbrl_data[f"https://data.sec.gov/api/xbrl/frames/{taxonomy}/{concept}/{unit}/{last_period}.json"]['data']:
            cik = item['cik']
            acc_no = item['accn'].replace('-','')  # Get acc_no for final results
            
            if logic in [">", "<", "=", "!=", ">=", "<="]:
                # Simple comparison for last period
                if compare_value(item['val'], logic, amount):
                    xbrl_matches.append(acc_no)
                    
            elif logic in ["increasing", "decreasing"]:
                # Get values across all periods using cik to track company
                values = get_company_values(xbrl_data, cik, periods)
                if check_trend(values, logic):
                    xbrl_matches.append(acc_no)  # But store acc_no in results
                    
            elif logic == "within_pct":
                values = get_company_values(xbrl_data, cik, periods)
                if check_within_range(values, amount):
                    xbrl_matches.append(acc_no)  # Store acc_no in results

        self.xbrl_matches.append((len(self.xbrl_matches), xbrl_matches))

    # submission callback is probably correct way even with http ranges.
    def process_submissions(self,
                            submission_callback=None):
        pass
        # make request to api # return cik and acco no
        # apply filters

        # apply sic filter if exists

        # apply search text filter if exists (accn)

        # apply xbrl filter if exists (accn)

        # grab data (1 method for datamule, 1 method for sec)

        # metadata callback

        # document callback
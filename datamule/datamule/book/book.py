# Streams data rather than downloading it. 
# additional functionality such as query by xbrl, and other db
# also this is basically our experimental rework of portfolio w/o disturbing existing users
# this is highly experimental and may not work as expected
# only for datamule source
# likely new bottleneck will be local parsing() - will be bypassed in future when we have parsed archive
# wow parsed archive is going to be crazy fast - like every 10k in 1 minute.

# example queries filter by sic = 7372, xbrl query = dei:operatingprofit > 0 in date range 2018-2019

# hmm do we go for sql esq or not.
# I think we do.
# i think we remove cik, ticker, sic, etc and just have a query object
# should be sql esq so users can use it easily w/o learnign new syntax

from .eftsquery import EFTSQuery
from .xbrlretriever import XBRLRetriever
from secsgml import parse_sgml_submission_into_memory
from ..helper import load_package_dataset, identifier_to_cik
from datetime import datetime


# maybe more like
# book = Book(cik=None,ticker=None,sic=None,submission_type=None,document_type=None,filing_date=None)
# book.filter_text()
# book.filter_xbrl()
# oh yeah thats simpler

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
            filing_date = ("2001-01-01",{datetime.now().strftime('%Y-%m-%d')})

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
        self.sic_matches = (sic_matches)

    def filter_xbrl(self,taxonomy, concept, unit, periods, logic, amount, callback=None):
        params = [{taxonomy:taxonomy,concept:concept,unit:unit,period:period} for period in periods]
        xbrl_data = self.XBRLRetriever.get_xbrl_frames(params)

        if callback is not None:
            callback(xbrl_data)

        if logic == '>':
            self.xbrl_matches = [item for item in xbrl_data if item['value'] > amount]
        elif logic == '<':
            self.xbrl_matches = [item for item in xbrl_data if item['value'] < amount]
        elif logic == '=':
            self.xbrl_matches = [item for item in xbrl_data if item['value'] == amount]
        elif logic == '>=':
            self.xbrl_matches = [item for item in xbrl_data if item['value'] >= amount]
        elif logic == '<=':
            self.xbrl_matches = [item for item in xbrl_data if item['value'] <= amount]
        elif logic == '!=':
            self.xbrl_matches = [item for item in xbrl_data if item['value'] != amount]
        
        self.xbrl_matches

        # we want to return item['accn']

        pass

    # submission callback is probably correct way even with http ranges.
    def process_submissions(self,
                            submission_callback=None):
        pass
        # apply filters

        # apply sic filter if exists

        # apply search text filter if exists (accn)

        # apply xbrl filter if exists (accn)

        # grab data (1 method for datamule, 1 method for sec)

        # metadata callback

        # document callback
from pkg_resources import resource_filename
import csv
import re

# May generalize to load any package resource
def _load_package_csv(name):
    """Load package CSV files"""
    csv_path = resource_filename('datamule', f'data/{name}.csv')
    company_tickers = []
    
    with open(csv_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            company_tickers.append(row)
    
    return company_tickers

def load_package_dataset(dataset):
    if dataset == 'company_tickers':
        return _load_package_csv('company_tickers')
    elif dataset =='company_former_names':
        return _load_package_csv('company_former_names')
    elif dataset =='company_metadata':
        return _load_package_csv('company_metadata')
    elif dataset == 'sec_glossary':
        return _load_package_csv('sec-glossary')
    elif dataset == 'xbrl_descriptions':
        return _load_package_csv('xbrl_descriptions')

def identifier_to_cik(ticker):
    """Convert company tickers to CIK codes"""
    company_tickers = _load_package_csv('company_tickers')
    if ticker:
        if isinstance(ticker, list):
            cik = []
            for t in ticker:
                cik.extend([company['cik'] for company in company_tickers if t == company['ticker']])
        else:
            cik = [company['cik'] for company in company_tickers if ticker == company['ticker']]

    if not cik:
        raise ValueError("No matching companies found")

    return cik


def fix_filing_url(url):
    match_suffix = re.search(r'/(\d{4})\.(.+?)$', url)
    if match_suffix:
        suffix_number = match_suffix.group(1)
        file_ext = match_suffix.group(2)
        match_accession = re.search(r'/(\d{18})/', url)
        if match_accession:
            accession_number = match_accession.group(1)
            formatted_accession_number = f"{accession_number[:10]}-{accession_number[10:12]}-{accession_number[12:]}"
            new_url = url.rsplit('/', 1)[0] + f'/{formatted_accession_number}-{suffix_number}.{file_ext}'
            return new_url
    return url

def convert_to_dashed_accession(accession):
    # Remove any existing dashes or whitespace
    cleaned = ''.join(accession.split())
    
    # Check if the cleaned string has 18 characters
    if len(cleaned) != 18:
        raise ValueError("Invalid accession number format. Expected 18 characters.")
    
    # Insert dashes at the correct positions
    dashed = f"{cleaned[:10]}-{cleaned[10:12]}-{cleaned[12:]}"
    
    return dashed

headers = {'User-Agent': 'John Smith johnsmith@gmail.com'}
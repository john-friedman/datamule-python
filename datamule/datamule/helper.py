from pkg_resources import resource_filename
import csv

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


def get_cik_from_dataset(dataset_name,key,value):
    dataset = load_package_dataset(dataset_name)
    cik = [company['cik'] for company in dataset if str(value) == company[key]]
    return cik

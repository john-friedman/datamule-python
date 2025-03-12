from pkg_resources import resource_filename
from functools import lru_cache
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

@lru_cache(maxsize=128)
def get_cik_from_dataset(dataset_name,key,value):
    dataset = load_package_dataset(dataset_name)
    cik = [company['cik'] for company in dataset if str(value) == company[key]]
    return cik



@lru_cache(maxsize=128)
def get_ciks_from_metadata_filters(**kwargs):
    """Get CIKs from company_metadata.csv that match all provided filters."""
    
    # Start with None to get all CIKs from first filter
    result_ciks = None
    
    # For each filter, get matching CIKs and keep intersection
    for key, value in kwargs.items():
        # Get CIKs for this filter
        ciks = get_cik_from_dataset('company_metadata', key, value)
        ciks = [int(cik) for cik in ciks]
        
        # If this is the first filter, set as initial result
        if result_ciks is None:
            result_ciks = set(ciks)
        # Otherwise, take intersection with previous results
        else:
            result_ciks &= set(ciks)
            
        # If no matches left, we can exit early
        if not result_ciks:
            return []
    
    return list(result_ciks)


def _process_cik_and_metadata_filters(cik=None, ticker=None, **kwargs):
        """ 
        Helper method to process CIK, ticker, and metadata filters.
        Returns a list of CIKs after processing.
        """
        # Input validation
        if cik is not None and ticker is not None:
            raise ValueError("Only one of cik or ticker should be provided, not both.")

        # Convert ticker to CIK if provided
        if ticker is not None:
            cik = get_cik_from_dataset('company_tickers', 'ticker', ticker)

        # Normalize CIK format
        if cik is not None:
            if isinstance(cik, str):
                cik = [int(cik)]
            elif isinstance(cik, int):
                cik = [cik]
            elif isinstance(cik, list):
                cik = [int(x) for x in cik]

        # Process metadata filters if provided
        if kwargs:
            metadata_ciks = get_ciks_from_metadata_filters(**kwargs)

            if cik is not None:
                cik = list(set(cik).intersection(metadata_ciks))
            else:
                cik = metadata_ciks
                
        return cik
        
from functools import lru_cache
import csv
from pathlib import Path
import os

def _load_package_csv(name):
    """Load CSV files from package data directory"""
    package_dir = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(package_dir,"datamule", "data", f"{name}.csv")
    
    data = []
    with open(csv_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            data.append(row)
    
    return data
    

def load_package_dataset(dataset):
    if dataset =='listed_filer_metadata':
        return _load_package_csv('listed_filer_metadata')

@lru_cache(maxsize=128)
def get_cik_from_dataset(dataset_name, key, value):
    dataset = load_package_dataset(dataset_name)
    
    if dataset_name == 'listed_filer_metadata' and key == 'ticker':
        key = 'tickers'
    
    result = []
    for company in dataset:
        if key in ['tickers', 'exchanges'] and dataset_name == 'listed_filer_metadata':
            # Parse the string representation of list into an actual list
            list_values = [i.strip() for i in company[key][1:-1].replace("'", "").replace('"', '').split(',')]
            if str(value) in list_values:
                result.append(company['cik'])
        elif str(value) == company[key]:
            result.append(company['cik'])
    
    return result

@lru_cache(maxsize=128)
def get_ciks_from_metadata_filters(**kwargs):
    """Get CIKs from listed_filer_metadata.csv that match all provided filters."""
    
    # Start with None to get all CIKs from first filter
    result_ciks = None
    
    # For each filter, get matching CIKs and keep intersection
    for key, value in kwargs.items():
        # Get CIKs for this filter
        ciks = get_cik_from_dataset('listed_filer_metadata', key, value)
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
    
    if 'tickers' in kwargs:
        raise ValueError("Use 'ticker' instead of 'tickers'.")

    # Convert ticker to CIK if provided
    if ticker is not None:
        if isinstance(ticker, str):
            ticker = [ticker]
            
        cik = []
        for t in ticker:
            ticker_ciks = get_cik_from_dataset('listed_filer_metadata', 'ticker', t)
            if ticker_ciks:
                cik.extend(ticker_ciks)

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
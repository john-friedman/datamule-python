from functools import lru_cache
from .datasets import _get_dataset


@lru_cache(maxsize=None)
def load_package_dataset(dataset):
    if dataset in ('listed_filer_metadata', 'unlisted_filer_metadata'):
        return tuple(_get_dataset(dataset))
    raise ValueError(f"Unknown dataset: {dataset}")

@lru_cache(maxsize=None)
def get_cik_from_dataset(dataset_name, key, value):
    dataset = load_package_dataset(dataset_name)
    
    if dataset_name == 'listed_filer_metadata' and key == 'ticker':
        key = 'tickers'
    
    result = []
    for company in dataset:
        if key in ['tickers', 'exchanges'] and dataset_name == 'listed_filer_metadata':
            list_values = [i.strip() for i in company[key][1:-1].replace("'", "").replace('"', '').split(',')]
            if str(value) in list_values:
                result.append(company['cik'])
        elif str(value) == company[key]:
            result.append(company['cik'])
    
    return result

@lru_cache(maxsize=128)
def get_ciks_from_metadata_filters(**kwargs):
    """Get CIKs from listed_filer_metadata that match all provided filters."""
    result_ciks = None
    
    for key, value in kwargs.items():
        ciks = get_cik_from_dataset('listed_filer_metadata', key, value)
        ciks = [int(cik) for cik in ciks]
        
        if result_ciks is None:
            result_ciks = set(ciks)
        else:
            result_ciks &= set(ciks)
            
        if not result_ciks:
            return []
    
    return list(result_ciks)

def _process_cik_and_metadata_filters(cik=None, ticker=None, **kwargs):
    if cik is not None and ticker is not None:
        raise ValueError("Only one of cik or ticker should be provided, not both.")
    
    if 'tickers' in kwargs:
        raise ValueError("Use 'ticker' instead of 'tickers'.")

    if ticker is not None:
        if isinstance(ticker, str):
            ticker = [ticker]
            
        cik = []
        for t in ticker:
            ticker_ciks = get_cik_from_dataset('listed_filer_metadata', 'ticker', t)
            if ticker_ciks:
                cik.extend(ticker_ciks)

        if len(cik) == 0:
            raise ValueError(f"No CIKs found for ticker: {ticker}")

    if cik is not None:
        if isinstance(cik, str):
            cik = [int(cik)]
        elif isinstance(cik, int):
            cik = [cik]
        elif isinstance(cik, list):
            cik = [int(x) for x in cik]

    if kwargs:
        metadata_ciks = get_ciks_from_metadata_filters(**kwargs)

        if cik is not None:
            cik = list(set(cik).intersection(metadata_ciks))
        else:
            cik = metadata_ciks
            
    return cik
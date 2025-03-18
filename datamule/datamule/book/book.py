from pathlib import Path
from ..helper import _process_cik_and_metadata_filters, load_package_dataset
from ..sec.xbrl.downloadcompanyfacts import download_company_facts

class Book:
    def __init__(self, path):
        self.path = Path(path)

    def download_xbrl(
        self, 
        cik=None, 
        ticker=None, 
        **kwargs
    ):
        # If no CIK or ticker specified, get all companies with tickers
        if cik is None and ticker is None:
            cik = [row['cik'] for row in load_package_dataset('company_tickers')]
            
        # Normalize cik to list format
        if isinstance(cik, (str, int)):
            cik = [cik]
            
        # Process CIK and metadata filters
        cik_list = _process_cik_and_metadata_filters(cik, ticker, **kwargs)
        
        # Download facts for all CIKs in parallel
        download_company_facts(cik=cik_list, output_dir=self.path)

    def query_345():
        pass
    def query_xbrl():
        pass
    def query_13fhr():
        pass
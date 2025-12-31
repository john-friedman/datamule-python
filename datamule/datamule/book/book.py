import os
from .s3transfer import s3_transfer as _s3_transfer
from .download_dataset_from_s3 import download_dataset as _download_dataset

class Book:
    def __init__(self, api_key=None):
        if api_key is not None:
            self._api_key = api_key

    @property
    def api_key(self):
        return getattr(self, '_api_key', None) or os.getenv('DATAMULE_API_KEY')

    @api_key.setter
    def api_key(self, value):
        if not value:
            raise ValueError("API key cannot be empty")
        self._api_key = value

    def s3_transfer(self, datamule_bucket, s3_credentials, max_workers=4, 
                    errors_json_filename='s3_transfer_errors.json', retry_errors=3,
                    force_daily=True, cik=None, submission_type=None, filing_date=None, 
                    api_key=None, accession=None):
        
        # Use provided key, or fall back to instance property
        api_key = api_key or self.api_key
        
        _s3_transfer(datamule_bucket=datamule_bucket, s3_credentials=s3_credentials, 
                    max_workers=max_workers, errors_json_filename=errors_json_filename, 
                    retry_errors=retry_errors, force_daily=force_daily, cik=cik, 
                    submission_type=submission_type, filing_date=filing_date, 
                    api_key=api_key, accession_number=accession)
        
    def download_dataset(self, dataset, filename=None, api_key=None):
        # Use provided key, or fall back to instance property
        api_key = api_key or self.api_key
        
        _download_dataset(dataset=dataset, filename=filename, api_key=api_key)
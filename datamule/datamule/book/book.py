from .s3transfer import s3_transfer

class Book:
    def __init__(self):
        pass

    def s3_transfer(self, datamule_bucket, s3_credentials, max_workers=4, errors_json_filename='s3_transfer_errors.json', retry_errors=3,
                    force_daily=True, cik=None, submission_type=None, filing_date=None, datamule_api_key=None,accession=None):
        
        s3_transfer(datamule_bucket=datamule_bucket, s3_credentials=s3_credentials, max_workers=max_workers, 
                          errors_json_filename=errors_json_filename, retry_errors=retry_errors,
                          force_daily=force_daily, cik=cik, submission_type=submission_type, 
                          filing_date=filing_date, datamule_api_key=datamule_api_key,accession_number=accession)
        

    def download_filings_processed_r2():
        pass


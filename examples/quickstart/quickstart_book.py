# This is code for interacting with datamule's s3 layer
# For example, say you want to ingest every SEC filing into your cloud to power Deep Search but using SEC filings which are higher trust.

from datamule import Book
import os


# Good practice to not hardcode your api keys
s3_credentials = {'s3_provider':'aws', # S3 Provider
                    'aws_access_key_id':os.environ['AWS_ACCESS_KEY_ID'],
                    'aws_secret_access_key':os.environ['AWS_SECRET_ACCESS_KEY'],
                    'region_name':'us-east-1', # Example region
                    'bucket_name':'mybucket'} # Your bucket name.


book = Book()

book.s3_transfer(datamule_bucket='filings_sgml_r2',s3_credentials=s3_credentials,force_daily=True,filing_date=('2025-09-03','2025-09-11'),
                 max_workers=128,errors_json_filename='s3_transfer_errors.json',retry_errors=3)
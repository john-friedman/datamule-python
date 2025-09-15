# Book

Book is a class for interacting with datamule's S3 Layer.


## `s3_transfer`

Transfer from datamule S3 to your S3 bucket.

Supported buckets:

- **filings_sgml_r2**: Every SEC submission in .sgml or .sgml.zst form. Type is included in metadata.

Supported providers:
- AWS

Easy to add more providers, if you have a preferred one please submit it [here](https://github.com/john-friedman/datamule-python/issues).

Note: If run locally from residential internet, this will likely be slow. Run in the cloud or on corporate internet.

### Example

Transfer to your S3
```python
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
```

### Parameters

- datamule_bucket: which datamule s3 bucket you want to transfer from.
- s3_credentials: dictionary of your bucket's credentials.
- force_daily: when set to True, constructs index of urls for one day, then transfers, and repeats. Otherwise, constructs index all at once.
- filing_date: subset by date. Supports start and end date tuple, list or string.
- submission_type: subset, e.g. by 10-K, or ['3','4','5'].
- datamule_api_key: If you have DATAMULE_API_KEY set to your environment it will be auto detected. This is for legacy purposes.
- retry_errors: How many times to retry a file in the transfer.
- errors_json_filename: filename of errors.
- max_workers: change depending on your machine to increase speed of transfers.
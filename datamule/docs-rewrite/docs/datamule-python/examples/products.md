# Products

Some features of datamule require an api_key. See [products](datamule.xyz/product).

## SEC Filings SGML R2

Downloads SEC filings from the SGML archive.
```
from datamule import Portfolio

portfolio = Portfolio('meta')
portfolio.download_submissions(ticker='META', submission_type='10-K', document_type='10-K', provider='datamule-sgml')
```

Transfers SEC filings to your S3 storage.
```
from datamule import Book
import os

book = Book()

book.s3_transfer(datamule_bucket='sec_filings_sgml_r2',s3_credentials=s3_credentials,force_daily=True,filing_date=('2025-09-03','2025-09-11'),
                 max_workers=128,errors_json_filename='s3_transfer_errors.json',retry_errors=3)
```


## SEC Filings TAR R2

Downloads SEC filings from the TAR archive. Newer than the SGML archive, and generally 20x faster.
```
from datamule import Portfolio

portfolio = Portfolio('meta')
portfolio.download_submissions(ticker='META', submission_type='10-K', document_type='10-K', provider='datamule-tar')
```

Transfers SEC filings to your S3 storage. Not implemented yet.

```
from datamule import Book
import os

book = Book()

book.s3_transfer(datamule_bucket='sec_filings_tar_r2',s3_credentials=s3_credentials,force_daily=True,filing_date=('2025-09-03','2025-09-11'),
                 max_workers=128,errors_json_filename='s3_transfer_errors.json',retry_errors=3)
```

## SEC Filings Lookup MySQL

Query SEC Filing metadata.
```
from datamule import Sheet

sheet = Sheet('lookup')
sheet.get_table('sec-filings-lookup',
    cik=320193,
    submissionType=['10-K', '10-Q'],
    filingDate=('2024-01-01', '2024-12-31'),
    containsXBRL=True,
    returnCols=['accessionNumber', 'cik', 'submissionType', 'filingDate', 'detectedTime'])
```

## SEC Filings Websocket

Get notified of new SEC filings in real time.
```
from datamule import Portfolio

portfolio = Portfolio('newfilings')

def data_callback(data):
    for item in data:
        print(item)

stream_submissions(data_callback=data_callback)
```

## SEC Filings Lookup S3

Not yet implemented.

## SEC Proxy Voting Records MySQL

Query proxy voting records.
```
from datamule import Sheet

sheet = Sheet('proxy')
results = sheet.get_table('proxy-voting-records',
    cusip='037833100',
    meetingDate=('2024-01-01', '2024-12-31'),
    howVoted='For')
print(results)
```

## SEC Proxy Voting Records S3

Not yet implemented.

## SEC Institutional Holdings MySQL
```
from datamule import Sheet

sheet = Sheet('sheet')
results = sheet.get_table('institutional-holdings',
    cusip='88160R101',
    sharesOrPrincipalAmount=('14000','14300')
    )
print(results)
```

## SEC Institutional Holdings S3

Not yet implemented.

## SEC Insider Transactions MySQL
```
from datamule import Sheet

sheet = Sheet('sheet')
results = sheet.get_table('insider-transactions',
    table='signature',
    signatureDate='2004-01-08')

print(results)
```

## SEC Insider Transactions S3

Not yet implemented.

## SEC XBRL S3

Not yet implemented.

## Simple XBRL S3

Not yet implemented.

## Fundamentals S3

Not yet implemented.

## Simple XBRL MySQL

```
from datamule import Sheet

sheet = Sheet('sheet')
results = sheet.get_table('simple-xbrl',
    accessionNumber=95017022000796)

print(results)
```

## Fundamentals MySQL

Not yet implemented.

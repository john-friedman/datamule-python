# Products

Some features of datamule require an api_key. See [products](https://datamule.xyz/product).

## Included Products

### SEC Filings SGML R2

Downloads SEC filings from the SGML archive.
```python
from datamule import Portfolio

portfolio = Portfolio('meta')
portfolio.download_submissions(ticker='META', submission_type='10-K', document_type='10-K', provider='datamule-sgml')
```

Transfers SEC filings to your S3 storage.
```python
from datamule import Book
import os

book = Book()

book.s3_transfer(datamule_bucket='filings_sgml_r2', s3_credentials=s3_credentials, force_daily=True, filing_date=('2025-09-03','2025-09-11'),
                 max_workers=128, errors_json_filename='s3_transfer_errors.json', retry_errors=3)
```

### SEC Filings TAR R2

Downloads SEC filings from the TAR archive. Newer than the SGML archive, and generally 20x faster.
```python
from datamule import Portfolio

portfolio = Portfolio('meta')
portfolio.download_submissions(ticker='META', submission_type='10-K', document_type='10-K', provider='datamule-tar')
```

### SEC Filings Lookup MySQL

Query SEC Filing metadata.
```python
from datamule import Sheet

sheet = Sheet('lookup')
sheet.get_table('sec-filings-lookup',
    cik=320193,
    submissionType=['10-K', '10-Q'],
    filingDate=('2024-01-01', '2024-12-31'),
    containsXBRL=True,
    returnCols=['accessionNumber', 'cik', 'submissionType', 'filingDate', 'detectedTime'])
```

### SEC Filings Websocket

Get notified of new SEC filings in real time.
```python
from datamule import Portfolio

portfolio = Portfolio('newfilings')

def data_callback(data):
    for item in data:
        print(item)

stream_submissions(data_callback=data_callback)
```

## Metadata Products

### SEC Submissions Details Table

Download filing metadata with submission types and dates.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='sec_submission_details_table'
)
```

### SEC Accession CIK Table

Download association table linking accession numbers to company CIKs.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='sec_accession_cik_table'
)
```

### SEC Documents Table

Download document-level details for all files within SEC filings.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='sec_documents_table'
)
```

### SEC Master Submissions Table

Download comprehensive master index of all SEC submissions.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='sec_master_submissions'
)
```

### SEC Accessions Master Index

Download newline-delimited text file of all accession numbers.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='sec_accessions'
)
```

## Proxy Voting Records Products

### SEC Proxy Voting Records MySQL

Query proxy voting records.
```python
from datamule import Sheet

sheet = Sheet('proxy')
results = sheet.get_table('proxy-voting-records',
    cusip='037833100',
    meetingDate=('2024-01-01', '2024-12-31'),
    howVoted='For')
print(results)
```

### Proxy Voting Records Table

Download proxy voting records showing how institutional investors voted.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='proxy_voting_records_table'
)
```

## Institutional Holdings Products

### SEC Institutional Holdings MySQL

Query institutional holdings.
```python
from datamule import Sheet

sheet = Sheet('sheet')
results = sheet.get_table('institutional-holdings',
    cusip='88160R101',
    sharesOrPrincipalAmount=('14000','14300'))
print(results)
```

### Institutional Holdings Table

Download 13F institutional holdings data.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='institutional_holdings_table'
)
```

## Insider Transactions Products

### SEC Insider Transactions MySQL

Query insider transactions.
```python
from datamule import Sheet

sheet = Sheet('sheet')
results = sheet.get_table('insider-transactions',
    table='signature',
    signatureDate='2004-01-08')
print(results)
```

### Insider Ownership Metadata Table

Download filing-level metadata for insider ownership reports.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='metadata_ownership_table'
)
```

### Insider Reporting Owner Table

Download reporting owner (insider) details.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='reporting_owner_ownership_table'
)
```

### Insider Non-Derivative Transactions Table

Download non-derivative security transactions (common stock, etc.).
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='non_derivative_transaction_ownership_table'
)
```

### Insider Non-Derivative Holdings Table

Download non-derivative security holdings.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='non_derivative_holding_ownership_table'
)
```

### Insider Derivative Transactions Table

Download derivative security transactions (options, warrants, etc.).
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='derivative_transaction_ownership_table'
)
```

### Insider Derivative Holdings Table

Download derivative security holdings.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='derivative_holding_ownership_table'
)
```

### Insider Owner Signatures Table

Download signature information for insider ownership filings.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='owner_signature_ownership_table'
)
```

## XBRL Products

### SEC XBRL S3

XBRL extracted from SEC filings.
```python
from datamule import Book

book = Book()
# Contact support for access details
```

### Simple XBRL MySQL

Query XBRL extracted from SEC filings in columnar format.
```python
from datamule import Sheet

sheet = Sheet('sheet')
results = sheet.get_table('simple-xbrl',
    accessionNumber=95017022000796)
print(results)
```

### Fundamentals S3

Fundamentals created from SEC filings.
```python
from datamule import Book

book = Book()
# Contact support for access details
```

### Fundamentals MySQL

Query fundamentals created from SEC filings.
```python
from datamule import Sheet

sheet = Sheet('sheet')
# Contact support for access details
```

### Simple XBRL Table

Download parsed XBRL facts from SEC filings.
```python
from datamule import Book

book = Book()
book.download_dataset(
    dataset='simple_xbrl_table'
)
```
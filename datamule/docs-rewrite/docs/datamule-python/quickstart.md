# Quickstart

## Installation
```
pip install datamule
```

## Basic Usage
### Portfolio
```
from datamule import Portfolio

# Create a Portfolio object
portfolio = Portfolio('output_dir') # can be an existing directory or a new one

# Download submissions
portfolio.download_submissions(
   filing_date=('2023-01-01','2023-01-03'),
   submission_type=['10-K']
)

# Iterate through documents by document type
for ten_k in portfolio.document_type('10-K'):
   ten_k.parse()
   print(ten_k.data['document']['part2']['item7'])

# For faster operations, you can take advantage of built in threading with callback function
def callback(submission):
   print(submission.path)

submission_results = portfolio.process_submissions(callback)
```

### Sheet
```
from datamule import Sheet

sheet = Sheet('apple')

sheet.download_xbrl(ticker='AAPL')
```

### Index
```
# Search for "risk factors" in Apple's 10-K filings
index = Index()
results = index.search_submissions(
    text_query='"risk factors"',
    submission_type="10-K",
    ticker="AAPL",
    filing_date=("2023-01-01","2023-01-31")
)

# Search for "war" but exclude "peace" in 10-K filings from January 2023 using 3 requests per second
results = index.search_submissions(
    text_query='war NOT peace',
    submission_type="10-K",
    filing_date=("2023-01-01","2023-01-31"),
    quiet=False,
    requests_per_second=3
)
```

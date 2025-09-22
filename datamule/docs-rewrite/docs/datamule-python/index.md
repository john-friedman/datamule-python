# datamule-python

Documentation for the python package.

???+ warning "This package is in beta"
    Things change frequently. If a change messes with your workflow, please [submit an issue](https://github.com/john-friedman/datamule-python/issues/new/choose).


# Notes on core classes (forthcoming)

## Portfolio
Deals with SEC filings. Downloads either using the SEC or datamule's archive. A datamule api key is required for datamule archive, and datamule websocket.

## Sheet (API_KEY required)
Deals with programmatic access to datamule's databases such as ownership or institutional holdings.

## Book (API_KEY required)
- Deals with programmatic access to datamule's S3 layer, for example getting text extracted from filings.
- s3_transfer(), simple function running locally on your machine that recieves presigned urls to copy into your s3 bucket.

## Index
Currently used to provide programmatic access to search the SEC by keyword. Will likely be rewritten as a general store of functions using sec.gov.

## Cloud (API_KEY required)
- Provides programmatic access to misc datamule APIs
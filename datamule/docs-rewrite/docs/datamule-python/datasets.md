# Datasets

Note: This page will get a major update soon. Other datasets not yet listed:

- when sec filings are detected: https://github.com/john-friedman/datamule-data/blob/master/data/datasets/detected_time_2025_12_03.csv.gz
- Filings erroneously marked as XBRL by the SEC https://github.com/john-friedman/datamule-data/blob/master/data/datasets/recorded_as_xbrl_but_no_xbrl.csv
- Every 10-K MDA up to 12/21/2025: https://github.com/john-friedman/Every-10-K-MDA-01-01-1993-12-21-2025.
- SEC Filing Wordcounts: https://github.com/john-friedman/sec-filing-wordcounts-1993-2000


## Usage
```python
from datamule.datasets import cik_cusip_crosswalk
import pandas as pd

print(pd.DataFrame(cik_cusip_crosswalk).head())
```

## Cloud
Datasets are stored in this [repository](https://github.com/john-friedman/datamule-data/tree/master/data/datasets) and are updated daily using GitHub Actions. 

## Local
Datasets are locally stored in the User's home. e.g. for Windows: `C:\Users\{username}\.datamule\datasets`.

## List of Datasets
* cik_cusip_crosswalk
* financial_security_identifiers_crosswalk
* proposal_results

## Updating Local Datasets
```python
from datamule.datasets import update_dataset
update_dataset('cik_cusip_crosswalk')
```
# Datasets

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

## Updating Local Datasets
```python
from datamule.datasets import update_dataset
update_dataset('cik_cusip_crosswalk')
```

## `get_ciks_from_tickers`

```
from datamule.utils.convenience import get_ciks_from_tickers
print(get_ciks_from_tickers(['IBM']))
```
```
[51143]
```

```
from datamule.utils.convenience import get_ciks_from_tickers
print(get_ciks_from_tickers(['TSLA','IBM']))
```
```
[1318605, 51143]
```

## construct_submissions_data
```
from datamule import construct_submissions_data

# what columns to extract. See https://data.sec.gov/submissions/CIK0001318605.json for full list
construct_submissions_data(
    "sec_master_submissions.csv",
    max_workers=8,
    batch_size=100,
    columns=[
        "accessionNumber",
        "filingDate",
        "form",
        "reportDate",
        "acceptanceDateTime",
        "act",
        "fileNumber",
        "filmNumber",
        "items",
        "size",
        "isXBRL",
        "isInlineXBRL",
    ],
)
```
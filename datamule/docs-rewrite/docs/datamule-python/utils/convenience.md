
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

## URL construction

```python
from datamule.utils.convenience import construct_index_url, construct_sgml_url, construct_folder_url, construct_document_url
cik = "878719"
accession = "000139834426000514"
filename = "idf66131687d57b800fc7cc59.jpg"

construct_index_url(accession)
# https://www.sec.gov/Archives/edgar/data/139834426000514/0001398344-26-000514-index.html

construct_sgml_url(accession,cik):
# https://www.sec.gov/Archives/edgar/data/878719/000139834426000514/0001398344-26-000514.txt

construct_folder_url(accession,cik)
# https://www.sec.gov/Archives/edgar/data/878719/000139834426000514/

construct_document_url(accession,cik,filename)
# https://www.sec.gov/Archives/edgar/data/878719/000139834426000514/idf66131687d57b800fc7cc59.jpg
```
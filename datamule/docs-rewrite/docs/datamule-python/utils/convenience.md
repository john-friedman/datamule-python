## `format_accession`

Converts accession numbers between three formats: `'int'`, `'dash'`, and `'no-dash'`. Input format is detected automatically.

```python
from datamule.utils.convenience import format_accession

format_accession("0001398344-26-000514", 'int')
# 139834426000514

format_accession(139834426000514, 'dash')
# '0001398344-26-000514'

format_accession("0001398344-26-000514", 'no-dash')
# '000139834426000514'
```

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

## `get_tickers_from_ciks`

```python
from datamule.utils.convenience import get_tickers_from_ciks
print(get_tickers_from_ciks([1318605]))
```
```
['TSLA']
```

```python
from datamule.utils.convenience import get_tickers_from_ciks
print(get_tickers_from_ciks([1318605, 51143]))
```
```
['TSLA', 'IBM']
```

## `get_company_names_from_ciks`

```python
from datamule.utils.convenience import get_company_names_from_ciks
print(get_company_names_from_ciks([1318605, 51143]))
```
```
['Tesla, Inc.', 'INTERNATIONAL BUSINESS MACHINES CORP']
```

## `get_sics_from_ciks`

```python
from datamule.utils.convenience import get_sics_from_ciks
print(get_sics_from_ciks([1318605, 51143]))
```
```
['3711', '7372']
```

## `get_adm0_from_ciks`

Returns the country of the company's business address. For US-based companies, returns `'United States of America'`.

```python
from datamule.utils.convenience import get_adm0_from_ciks
print(get_adm0_from_ciks([1318605, 51143]))
```
```
['United States of America', 'United States of America']
```

## `get_us_state_from_ciks`

Returns the two-letter US state code for US-based companies. Returns `''` for non-US companies.

```python
from datamule.utils.convenience import get_us_state_from_ciks
print(get_us_state_from_ciks([1318605, 51143]))
```
```
['TX', 'NY']
```

## `get_us_zipcodes_from_ciks`

Returns the ZIP code for US-based companies. Returns `None` for non-US companies.

```python
from datamule.utils.convenience import get_us_zipcodes_from_ciks
print(get_us_zipcodes_from_ciks([1318605, 51143]))
```
```
['78725', '10504']
```

## `get_business_street1_from_ciks`

```python
from datamule.utils.convenience import get_business_street1_from_ciks
print(get_business_street1_from_ciks([1318605, 51143]))
```
```
['1 TESLA ROAD', '1 NEW ORCHARD ROAD']
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
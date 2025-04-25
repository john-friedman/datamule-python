# Table

Tables are created by flattening '.xml' documents. One '.xml' document may have many tables.

## Attributes
* `table.type` - table type e.g. `non_derivative_holding_ownership`
* `table.accession` - submission accession number
* `table.columns` - table's columns
* `table.data` - table data in a list of dictionaries. 

## Quickstart

```
from datamule import Portfolio
portfolio = Portfolio('345')
portfolio.download_submissions(filing_date=('2020-01-01','2020-01-01'),submission_type=['3','4','5'])
for document in portfolio.document_type(['3','4','5']):
    document.write_csv(output_folder='ownership')
```

???+ note "Table is new"
    Will make the UI better, likely improvements include passing as iterable
# Table

Tables are created by flattening '.xml' documents. One '.xml' document may have many tables.

## Attributes
* `table.type` - table type e.g. `non_derivative_holding_ownership`
* `table.accession` - submission accession number
* `table.columns` - table's columns
* `table.data` - table data in a list of dictionaries. 

???+ note "Table is new"
    Will make the UI better, likely improvements include passing as iterable
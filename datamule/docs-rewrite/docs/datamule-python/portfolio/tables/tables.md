# Tables

Tables are created by flattening '.xml' documents. One '.xml' document may have many tables.

`attributes`:

- `tables` - list of `Table` objects, each representing a parsed table from the document.

## Table

`attributes`:

- `name` - name of the table
- `accession` - accession number of the submission
- `data` - parsed table data as a list of dictionaries

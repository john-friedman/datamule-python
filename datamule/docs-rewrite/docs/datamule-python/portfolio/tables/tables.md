# Tables

`attributes`:

- `tables` - list of `Table` objects, each representing a parsed table from the document.

## Table

`attributes`:

- `name` - name of the table
- `accession` - accession number of the submission
- `data` - parsed table data as a list of dictionaries
- `description` - description of the table. For example, tables extracted from html files will use the adjacent context or title above the table as description.

## Example

Table 'extracted_table' (0001144204-11-059106) - 4 rows
description: Golden Parachute Compensation Table

|                                                                         | Cash(1) | Equity ($)(2) | Pension/ NQDC ($) | Perquisites/ Benefits ($) | Tax Reimbursements ($) | Other ($) | Total ($) |
|-------------------------------------------------------------------------|---------|---------------|-------------------|---------------------------|------------------------|-----------|-----------|
| Richard W. Turner Chairman & Chief Executive Officer                    | 450,000 | 1,840,000     | —                 | —                         | —                      | —         | 2,290,000 |
| Thomas W. Fry Sr. Vice President, Chief Financial Officer and Secretary | 210,000 | 258,620       | —                 | —                  
       | —                      | —         | 468,620   |
| Stephen B. Goldberg— Executive Vice President & President of CMHS       | —       | 128,750       | —                 | —                  
       | —                      | —         | 128,750   |

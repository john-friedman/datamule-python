# Sheet

Sheet is a class for downloading and working with tabular datasets from the SEC.

???+ note "7/23/25 Update"
    Sheet is being remade to interact with datamule-cloud features. Old functionality will move to a new class.

## get_table

Access datamule's MySQL RDS offerings.

```python
get_table(self, table, cik=None, ticker=None, **kwargs)
```

### Databases

#### Lookup Database
All tables use the lookup database's parameters for filtering before the main query.

**accession_cik**

- accessionNumber: BIGINT UNSIGNED NOT NULL
- cik: BIGINT UNSIGNED NOT NULL
- Primary Key: Composite key on (accessionNumber, cik)
- Index: idx_cik on cik column

**submission_details**

- accessionNumber: BIGINT UNSIGNED PRIMARY KEY
- submissionType: VARCHAR(16) NOT NULL
- filingDate: DATE NOT NULL
- isInlineXBRL: BOOLEAN NOT NULL DEFAULT FALSE
- Indexes: idx_submission_filing, idx_filing_date, idx_inline_xbrl

Example:
```python
print(sheet.get_table('accession_cik', ticker=['F']))
```

#### Simple XBRL

**simple_xbrl**

- id: BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- accessionNumber: BIGINT UNSIGNED NOT NULL
- context_id: INT UNSIGNED NOT NULL
- taxonomy: VARCHAR(16) NOT NULL
- name: VARCHAR(256) NOT NULL
- value: TEXT NOT NULL
- period_start_date: DATE NOT NULL
- period_end_date: DATE NOT NULL
- Indexes: Multiple indexes on accession, taxonomy, name, and period combinations

Examples:
```python
ford_netincome = sheet.get_table('simple_xbrl', taxonomy="us-gaap", 
                                name="NetIncomeLoss", ticker=['META'])

jan_2020 = sheet.get_table('simple_xbrl', taxonomy="us-gaap", 
                          name="NetIncomeLoss", 
                          filingDate=('2020-01-01','2020-01-31'))
```
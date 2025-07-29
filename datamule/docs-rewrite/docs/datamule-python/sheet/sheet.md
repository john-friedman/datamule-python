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
- PRIMARY KEY: (accessionNumber, cik)
- Indexes:
    - idx_cik (cik)

**submission_details**

- accessionNumber: BIGINT UNSIGNED PRIMARY KEY
- submissionType: VARCHAR(16) NOT NULL
- filingDate: DATE NOT NULL
- isInlineXBRL: BOOLEAN NOT NULL DEFAULT FALSE
- isXBRL: BOOLEAN NOT NULL DEFAULT FALSE
- Indexes:
    - idx_submission_filing (submissionType, filingDate)
    - idx_filing_date (filingDate)
    - idx_inline_xbrl (isInlineXBRL)
    - idx_xbrl (isXBRL)


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
- period_start_date: DATE
- period_end_date: DATE
- members: TEXT
- Indexes:
    - idx_accession_name (accessionNumber, name)
    - idx_accession_period_range (accessionNumber, period_start_date, period_end_date)
    - idx_accession_taxonomy_name (accessionNumber, taxonomy, name)
    - idx_taxonomy_name (taxonomy, name)
    - idx_period_range (period_start_date, period_end_date)
    - idx_accession_name_members (accessionNumber, name, members(255))

Examples:
```python
ford_netincome = sheet.get_table('simple_xbrl', taxonomy="us-gaap", 
                                name="NetIncomeLoss", ticker=['META'])

jan_2020 = sheet.get_table('simple_xbrl', taxonomy="us-gaap", 
                          name="NetIncomeLoss", 
                          filingDate=('2020-01-01','2020-01-31'))

sheet.get_table('simple_xbrl', filingDate=('2024-01-01','2024-01-31'),members=['us-gaap:CommonStockMember','exch:XCHI'])
```

#### Fundamentals

**fundamentals**

Fundamentals is a convenience function that uses [company-fundamentals](https://github.com/john-friedman/company-fundamentals) to construct fundamentals on the fly using **simple_xbrl**.

Full list of fundamentals [here](https://github.com/john-friedman/company-fundamentals/blob/master/company_fundamentals/calculations/calculations.py).

Example:
```
print(sheet.get_table('fundamentals',fundamentals=['freeCashFlow'],ticker=['TSLA'],filingDate=('2020-01-01','2020-12-31'),
      submissionType='10-K'))
```
Result
```
{'CashFlowStatement': {'freeCashFlow': [{'value': 1078000000.0, 'period_start_date': '2019-01-01T00:00:00.000Z', 'period_end_date': '2019-12-31T00:00:00.000Z'}, {'value': -3000000.0, 'period_start_date': '2018-01-01T00:00:00.000Z', 'period_end_date': '2018-12-31T00:00:00.000Z'}, {'value': -3354000000.0, 'period_start_date': '2017-01-01T00:00:00.000Z', 'period_end_date': '2017-12-31T00:00:00.000Z'}]}}
```

#### Proxy Voting Records

**proxy_voting_record**

- id: BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- accessionNumber: BIGINT UNSIGNED NOT NULL
- meetingDate: DATE
- managementRecommendation: VARCHAR(16)
- sharesVoted: BIGINT UNSIGNED
- howVoted: VARCHAR(16)
- sharesOnLoan: BIGINT UNSIGNED
- cusip: CHAR(9)
- issuerName: VARCHAR(256)
- categoryType: VARCHAR(256)
- voteDescription: VARCHAR(8192)
- Indexes:
    - idx_cusip (cusip)
    - idx_meeting_date (meetingDate)
    - idx_category_type (categoryType)
    - idx_management_recommendation (managementRecommendation)
    - idx_how_voted (howVoted)
    - idx_shares_voted (sharesVoted)
    - idx_issuer_name (issuerName)
    - idx_accession_number (accessionNumber)

Examples:
```python
# Get voting records for a date range
recent_votes = sheet.get_table('proxy_voting_record', 
                              meetingDate=('2023-01-01', '2023-01-31'))

# Filter by voting behavior
against_mgmt = sheet.get_table('proxy_voting_record', 
                              managementRecommendation='For',
                              howVoted='Against', 
                              meetingDate=('2023-01-01', '2023-01-31'))


# Get executive compensation votes
exec_comp = sheet.get_table('proxy_voting_record', 
                           categoryType='COMPENSATION',cik='2024532')
```
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

#### Lookup
All tables use the lookup database's parameters for filtering before the main query.

Sources:
- SEC's public EDGAR filing history for all filers from the Submissions API. Recompiled nightly. [ZIP](https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip)

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

Sources:
- All submissions containing inline XBRL or XBRL.

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

Sources:
- All submissions containing inline XBRL or XBRL.

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

Sources:
- Submission Type: N-PX, N-PX/A. Document Type: PROXY VOTING RECORD.

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

#### 13F-HR

**information_table**

Sources:
- Submission Type: 13F-HR, 13F-HR/A. Document Type: INFORMATION TABLE.

- id: BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- accessionNumber: BIGINT UNSIGNED NOT NULL
- nameOfIssuer: VARCHAR(256)
- titleOfClass: VARCHAR(256)
- cusip: CHAR(9)
- value: BIGINT UNSIGNED
- sharesOrPrincipalAmount: BIGINT UNSIGNED
- sharesOrPrincipalAmountType: VARCHAR(16)
- investmentDiscretion: VARCHAR(16)
- votingAuthoritySole: BIGINT UNSIGNED
- votingAuthorityShared: BIGINT UNSIGNED
- votingAuthorityNone: BIGINT UNSIGNED
- putCall: VARCHAR(16)
- otherManager: VARCHAR(256)
- Indexes:
    - idx_cusip (cusip)
    - idx_accession_number (accessionNumber)
    - idx_voting_authority (votingAuthoritySole, votingAuthorityShared, votingAuthorityNone)
    - idx_name_of_issuer (nameOfIssuer)
    - idx_title_of_class (titleOfClass)
    - idx_value (value)
    - idx_shares_or_principal_amount (sharesOrPrincipalAmount)
    - idx_shares_or_principal_amount_type (sharesOrPrincipalAmountType)
    - idx_investment_discretion (investmentDiscretion)

Examples:
```python

# Find all holdings of a specific security by CUSIP
aapl_holders = sheet.get_table('information_table', cusip='037833100',filingDate=('2024-01-01', '2024-01-07'))
```

#### Ownership

Sources:
- Submission Type: 3, 4, 5, 3/A, 4/A and 5/A. Document Type: 3, 4, 5, 3/A, 4/A and 5/A.


**derivative_holding_ownership**

- id: BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- accessionNumber: BIGINT UNSIGNED NOT NULL
- securityTitle: VARCHAR(128)
- securityTitleFootnote: TEXT
- conversionOrExercisePrice: BIGINT UNSIGNED
- conversionOrExercisePriceFootnote: TEXT
- exerciseDate: DATE
- exerciseDateFootnote: TEXT
- expirationDate: DATE
- expirationDateFootnote: TEXT
- underlyingSecurityTitle: VARCHAR(128)
- underlyingSecurityTitleFootnote: TEXT
- underlyingSecurityShares: BIGINT UNSIGNED
- underlyingSecuritySharesFootnote: TEXT
- underlyingSecurityValue: BIGINT UNSIGNED
- underlyingSecurityValueFootnote: TEXT
- directOrIndirectOwnership: CHAR(1)
- directOrIndirectOwnershipFootnote: TEXT
- natureOfOwnership: VARCHAR(256)
- natureOfOwnershipFootnote: TEXT
- sharesOwnedFollowingTransaction: BIGINT UNSIGNED
- sharesOwnedFollowingTransactionFootnote: TEXT
- valueOwnedFollowingTransaction: BIGINT UNSIGNED
- valueOwnedFollowingTransactionFootnote: TEXT
- transactionFormType: TINYINT
- transactionCodingFootnote: TEXT
- Indexes:
    - idx_accession_number (accessionNumber)
    - idx_underlying_security_title (underlyingSecurityTitle)
    - idx_expiration_date (expirationDate)
    - idx_security_title (securityTitle)

**derivative_transaction_ownership**

- id: BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- accessionNumber: BIGINT UNSIGNED NOT NULL
- securityTitle: VARCHAR(128)
- securityTitleFootnote: TEXT
- conversionOrExercisePrice: BIGINT UNSIGNED
- conversionOrExercisePriceFootnote: TEXT
- transactionDate: DATE
- transactionDateFootnote: TEXT
- deemedExecutionDate: DATE
- deemedExecutionDateFootnote: TEXT
- transactionFormType: TINYINT
- transactionCode: CHAR(1)
- equitySwapInvolved: VARCHAR(8)
- transactionCodingFootnote: TEXT
- transactionShares: BIGINT UNSIGNED
- transactionSharesFootnote: TEXT
- transactionPricePerShare: BIGINT UNSIGNED
- transactionPricePerShareFootnote: TEXT
- transactionAcquiredDisposedCode: CHAR(1)
- transactionTotalValue: BIGINT UNSIGNED
- transactionTotalValueFootnote: TEXT
- exerciseDate: DATE
- exerciseDateFootnote: TEXT
- expirationDate: DATE
- expirationDateFootnote: TEXT
- underlyingSecurityTitle: VARCHAR(128)
- underlyingSecurityTitleFootnote: TEXT
- underlyingSecurityShares: BIGINT UNSIGNED
- underlyingSecuritySharesFootnote: TEXT
- underlyingSecurityValue: BIGINT UNSIGNED
- sharesOwnedFollowingTransaction: BIGINT UNSIGNED
- sharesOwnedFollowingTransactionFootnote: TEXT
- directOrIndirectOwnership: CHAR(1)
- directOrIndirectOwnershipFootnote: TEXT
- natureOfOwnership: VARCHAR(256)
- natureOfOwnershipFootnote: TEXT
- transactionTimeliness: CHAR(1)
- transactionTimelinessFootnote: TEXT
- valueOwnedFollowingTransaction: BIGINT UNSIGNED
- valueOwnedFollowingTransactionFootnote: TEXT
- transactionAcquiredDisposedCodeFootnote: TEXT
- underlyingSecurityValueFootnote: TEXT
- Indexes:
    - idx_accession_number (accessionNumber)
    - idx_transaction_date (transactionDate)
    - idx_transaction_code (transactionCode)
    - idx_underlying_security_title (underlyingSecurityTitle)
    - idx_expiration_date (expirationDate)

**metadata_ownership**

- id: BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- accessionNumber: BIGINT UNSIGNED NOT NULL
- periodOfReport: DATE
- issuerCik: BIGINT UNSIGNED
- issuerName: VARCHAR(128)
- issuerTradingSymbol: VARCHAR(16)
- documentType: VARCHAR(8)
- remarks: TEXT
- documentDescription: TEXT
- footnotes: TEXT
- notSubjectToSection16: VARCHAR(8)
- form3HoldingsReported: TINYINT
- form4TransactionsReported: TINYINT
- noSecuritiesOwned: TINYINT
- aff10b5One: VARCHAR(8)
- dateOfOriginalSubmission: DATE
- schemaVersion: VARCHAR(8)
- Indexes:
    - idx_accession_number (accessionNumber)
    - idx_issuer_cik (issuerCik)
    - idx_period_of_report (periodOfReport)

**non_derivative_holding_ownership**

- id: BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- accessionNumber: BIGINT UNSIGNED NOT NULL
- securityTitle: VARCHAR(128)
- securityTitleFootnote: TEXT
- sharesOwnedFollowingTransaction: BIGINT UNSIGNED
- sharesOwnedFollowingTransactionFootnote: TEXT
- directOrIndirectOwnership: CHAR(1)
- directOrIndirectOwnershipFootnote: TEXT
- natureOfOwnership: VARCHAR(256)
- natureOfOwnershipFootnote: TEXT
- valueOwnedFollowingTransaction: BIGINT UNSIGNED
- transactionCodingFootnote: TEXT
- transactionFormType: TINYINT
- valueOwnedFollowingTransactionFootnote: TEXT
- Indexes:
    - idx_accession_number (accessionNumber)
    - idx_security_title (securityTitle)
    - idx_direct_or_indirect_ownership (directOrIndirectOwnership)

**non_derivative_transaction_ownership**

- id: BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- accessionNumber: BIGINT UNSIGNED NOT NULL
- securityTitle: VARCHAR(128)
- securityTitleFootnote: TEXT
- transactionDate: DATE
- transactionDateFootnote: TEXT
- deemedExecutionDate: DATE
- deemedExecutionDateFootnote: TEXT
- transactionFormType: TINYINT
- transactionCode: CHAR(1)
- equitySwapInvolved: VARCHAR(8)
- transactionCodingFootnote: TEXT
- transactionShares: BIGINT UNSIGNED
- transactionSharesFootnote: TEXT
- transactionPricePerShare: BIGINT UNSIGNED
- transactionPricePerShareFootnote: TEXT
- transactionAcquiredDisposedCode: CHAR(1)
- transactionAcquiredDisposedCodeFootnote: TEXT
- sharesOwnedFollowingTransaction: BIGINT UNSIGNED
- sharesOwnedFollowingTransactionFootnote: TEXT
- directOrIndirectOwnership: CHAR(1)
- directOrIndirectOwnershipFootnote: TEXT
- natureOfOwnership: VARCHAR(256)
- natureOfOwnershipFootnote: TEXT
- transactionTimeliness: CHAR(1)
- transactionTimelinessFootnote: TEXT
- valueOwnedFollowingTransaction: BIGINT UNSIGNED
- valueOwnedFollowingTransactionFootnote: TEXT
- Indexes:
    - idx_accession_number (accessionNumber)
    - idx_transaction_date (transactionDate)
    - idx_transaction_code (transactionCode)
    - idx_transaction_acquired_disposed_code (transactionAcquiredDisposedCode)
    - idx_security_title (securityTitle)

**owner_signature_ownership**

- id: BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- accessionNumber: BIGINT UNSIGNED NOT NULL
- signatureName: VARCHAR(256)
- signatureDate: DATE
- Indexes:
    - idx_accession_number (accessionNumber)
    - idx_signature_date (signatureDate)
    - idx_signature_name (signatureName)

**reporting_owner_ownership**

- id: BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- accessionNumber: BIGINT UNSIGNED NOT NULL
- rptOwnerCity: VARCHAR(64)
- rptOwnerState: VARCHAR(4)
- rptOwnerStateDescription: VARCHAR(64)
- rptOwnerStreet1: VARCHAR(64)
- rptOwnerStreet2: VARCHAR(64)
- rptOwnerZipCode: VARCHAR(16)
- rptOwnerCik: BIGINT UNSIGNED
- rptOwnerName: VARCHAR(256)
- rptOwnerIsDirector: VARCHAR(8)
- rptOwnerIsOfficer: VARCHAR(8)
- rptOwnerIsTenPercentOwner: VARCHAR(8)
- rptOwnerIsOther: VARCHAR(8)
- rptOwnerOfficerTitle: VARCHAR(64)
- rptOwnerOtherText: VARCHAR(64)
- Indexes:
    - idx_accession_number (accessionNumber)
    - idx_rpt_owner_name (rptOwnerName)
    - idx_rpt_owner_is_director (rptOwnerIsDirector)
    - idx_rpt_owner_is_officer (rptOwnerIsOfficer)
    - idx_rpt_owner_is_ten_percent_owner (rptOwnerIsTenPercentOwner)
    - idx_rpt_owner_is_other (rptOwnerIsOther)
    - idx_rpt_owner_officer_title (rptOwnerOfficerTitle)

Examples:
```python
# Get all Tesla insider transactions for a date range
tesla_transactions = sheet.get_table('non_derivative_transaction_ownership', 
                                    ticker=['TSLA'], 
                                    transactionDate=('2024-01-01', '2024-03-31'))

# Find all stock options expiring soon
expiring_options = sheet.get_table('derivative_holding_ownership',
                                  expirationDate=('2024-12-01', '2024-12-31'))

# Get reporting owner details for specific filings
owner_info = sheet.get_table('reporting_owner_ownership',
                            cik=['1318605'])  # Tesla CIK

# Find all buy transactions (A = Acquired)
buy_transactions = sheet.get_table('non_derivative_transaction_ownership',
                                  transactionAcquiredDisposedCode='A',
                                  transactionDate=('2024-01-01', '2024-01-31'))

# Get metadata for all Form 4 filings
form4_metadata = sheet.get_table('metadata_ownership',
                                 documentType='4',
                                 periodOfReport=('2024-01-01', '2024-01-31'))
```
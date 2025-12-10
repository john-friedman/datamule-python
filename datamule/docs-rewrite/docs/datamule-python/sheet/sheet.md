# Sheet

Sheet is a class for downloading and working with tabular datasets constructed from SEC filings. It requires a [datamule api_key](https://datamule.xyz/dashboard2).

Sheet is in beta. If you would like to suggest better indices or query patterns, my email is [johnfriedman@datamule.xyz?subject=[Sheet Feature Request]](mailto:johnfriedman@datamule.xyz). Or submit a [GitHub issue](https://github.com/john-friedman/datamule-python/issues/new).

## get_table

Access datamule's MySQL RDS offerings.

```python
get_table(self, database, **kwargs)
```

## Databases

### R2 Archive

Query SEC filings archive to get accession numbers matching specific criteria. Returns only accession numbers for matched filings.

```python
sheet.get_table('r2-archive',
    cik=320193,
    submissionType='10-K',
    filingDate=('2024-01-01', '2024-12-31'),
    containsXBRL=True)
```

#### Schema

**Database:** `sec_filings_lookup`

Queries across three tables:
- `sec_submission_details_table` - Filing metadata
- `sec_accession_cik_table` - CIK associations
- `sec_documents_table` - Document details (conditionally joined)

**Returns:** Array of accession numbers matching the query criteria.

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `cik` | int / list[int] | Filter by company CIK |
| `accessionNumber` | int / list[int] | Filter by accession number(s) |
| `submissionType` | str / list[str] | Filter by form type |
| `filingDate` | str / list[str] / tuple(str, str) | Filing date(s) or range |
| `reportDate` | str / list[str] / tuple(str, str) | Report date(s) or range |
| `detectedTime` | tuple(str, str) | Detected time range |
| `containsXBRL` | bool | Filter by XBRL presence |
| `documentType` | str / list[str] | Filter by document type |
| `filename` | str | LIKE match on filename |
| `sequence` | int / list[int] | Filter by document sequence |
| `page` | int | Page number (default: 1) |
| `pageSize` | int | Records per page (max: 25000) |

### SEC Filings Lookup

Metadata for SEC filings including submission details, CIKs, and document information.

```python
sheet.get_table('sec-filings-lookup',
    cik=320193,
    submissionType=['10-K', '10-Q'],
    filingDate=('2024-01-01', '2024-12-31'),
    containsXBRL=True,
    returnCols=['accessionNumber', 'cik', 'submissionType', 'filingDate'])
```

#### Schema

**Database:** `sec_filings_lookup`

##### sec_submission_details_table

| Column | Type | Description |
|--------|------|-------------|
| `accessionNumber` | BIGINT UNSIGNED | Primary key |
| `submissionType` | VARCHAR(16) | Form type (e.g., '10-K', '10-Q') |
| `filingDate` | DATE | Date filed with SEC |
| `reportDate` | DATE | Period end date |
| `detectedTime` | DATETIME | When filing was detected |
| `containsXBRL` | BOOLEAN | Whether filing includes XBRL data |

**Indexes:**
- PRIMARY KEY: `accessionNumber`
- `idx_submission_filing`, `idx_filing_date`, `idx_time`, `idx_xbrl`

##### sec_accession_cik_table

| Column | Type | Description |
|--------|------|-------------|
| `accessionNumber` | BIGINT UNSIGNED | SEC accession number |
| `cik` | BIGINT UNSIGNED | Company CIK |

**Indexes:**
- PRIMARY KEY: `(accessionNumber, cik)`
- `idx_cik`

##### sec_documents_table

| Column | Type | Description |
|--------|------|-------------|
| `accessionNumber` | BIGINT UNSIGNED | SEC accession number |
| `documentType` | VARCHAR(128) | Document type |
| `sequence` | SMALLINT | Document sequence number |
| `filename` | VARCHAR(500) | Document filename |
| `description` | VARCHAR(1000) | Document description |
| `secsgmlSizeBytes` | INT | Document size in bytes |

**Indexes:**
- PRIMARY KEY: `(accessionNumber, sequence)`
- `idx_document_filename`

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `cik` | int / list[int] | Filter by company CIK |
| `accessionNumber` | int / list[int] | Filter by accession number(s) |
| `submissionType` | str / list[str] | Filter by form type |
| `filingDate` | str / list[str] / tuple(str, str) | Filing date(s) or range |
| `reportDate` | str / list[str] / tuple(str, str) | Report date(s) or range |
| `detectedTime` | tuple(str, str) | Detected time range |
| `containsXBRL` | bool | Filter by XBRL presence |
| `documentType` | str / list[str] | Filter by document type |
| `filename` | str | LIKE match on filename |
| `sequence` | int / list[int] | Filter by document sequence |
| `returnCols` | list[str] | Columns to return (default: all) |
| `page` | int | Page number (default: 1) |
| `pageSize` | int | Records per page (max: 25000) |

### Simple XBRL

Parsed XBRL facts from SEC filings. XBRL is a standardized format for financial reporting data.

```python
sheet.get_table('simple-xbrl',
    accessionNumber=1234567890,
    taxonomy='us-gaap',
    namePattern='Revenue',
    periodDate=('2024-01-01', '2024-12-31'),
    hasValue=True)
```

#### Schema

**Database:** `simple_xbrl`  
**Table:** `simple_xbrl_table`

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT UNSIGNED | Auto-increment primary key |
| `accessionNumber` | BIGINT UNSIGNED | SEC filing accession number |
| `context_id` | BIGINT UNSIGNED | XBRL context identifier |
| `taxonomy` | VARCHAR(16) | Taxonomy namespace (e.g., 'us-gaap', 'dei') |
| `name` | VARCHAR(256) | XBRL element name |
| `value` | TEXT | The reported value |
| `period_start_date` | DATE | Start date of the reporting period |
| `period_end_date` | DATE | End date of the reporting period |
| `members` | TEXT | Dimensional members/axes information |

**Indexes:**
- PRIMARY KEY: `(id, accessionNumber)`
- `idx_accession`, `idx_taxonomy_name`, `idx_period`

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `accessionNumber` | int / list[int] | Filter by accession number(s) |
| `taxonomy` | str / list[str] | Filter by taxonomy |
| `contextId` | int / list[int] | Filter by context ID |
| `name` | str / list[str] | Exact match on element name |
| `namePattern` | str | LIKE match on element name |
| `periodStartDate` | str / list[str] | Exact match on start date |
| `periodEndDate` | str / list[str] | Exact match on end date |
| `periodDate` | tuple(str, str) | Date range (finds overlapping periods) |
| `instantDate` | str / list[str] | Facts where start = end date |
| `members` | str / list[str] | Exact match on members |
| `membersPattern` | str | LIKE match on members |
| `hasValue` | bool | Filter by presence of value |
| `hasPeriod` | bool | Duration (True) vs instant (False) |
| `page` | int | Page number (default: 1) |
| `pageSize` | int | Records per page (max: 25000) |

### Institutional Holdings

13F institutional holdings data showing equity positions held by institutional investment managers.

```python
sheet.get_table('institutional-holdings',
    accessionNumber=1234567890,
    cusip='037833100',
    value=(1000000, None),
    investmentDiscretion='SOLE')
```

#### Schema

**Database:** `institutional_holdings`  
**Table:** `institutional_holdings_table`

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT UNSIGNED | Auto-increment primary key |
| `accessionNumber` | BIGINT UNSIGNED | SEC filing accession number |
| `cusip` | CHAR(9) | Security CUSIP identifier |
| `nameOfIssuer` | VARCHAR(256) | Name of the security issuer |
| `titleOfClass` | VARCHAR(256) | Class of security |
| `value` | BIGINT UNSIGNED | Position value in dollars |
| `sharesOrPrincipalAmount` | BIGINT UNSIGNED | Number of shares or principal amount |
| `sharesOrPrincipalAmountType` | VARCHAR(16) | Type: 'SH' (shares) or 'PRN' (principal) |
| `investmentDiscretion` | VARCHAR(16) | Investment discretion type |
| `putCall` | VARCHAR(16) | Put or call option indicator |
| `otherManager` | VARCHAR(256) | Other managers with shared voting authority |
| `votingAuthoritySole` | BIGINT UNSIGNED | Shares with sole voting authority |
| `votingAuthorityShared` | BIGINT UNSIGNED | Shares with shared voting authority |
| `votingAuthorityNone` | BIGINT UNSIGNED | Shares with no voting authority |

**Indexes:**
- PRIMARY KEY: `(id, accessionNumber)`
- `idx_accession`, `idx_cusip`, `idx_issuer`, `idx_value`, `idx_cusip_value`

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `accessionNumber` | int / list[int] | Filter by accession number(s) |
| `cusip` | str / list[str] | Filter by CUSIP |
| `nameOfIssuer` | str / list[str] | Exact match on issuer name |
| `nameOfIssuerPattern` | str | LIKE match on issuer name |
| `titleOfClass` | str / list[str] | Exact match on security class |
| `titleOfClassPattern` | str | LIKE match on security class |
| `value` | int / list[int] / tuple(int, int) | Position value(s) or range |
| `sharesOrPrincipalAmount` | int / list[int] / tuple(int, int) | Shares/principal or range |
| `sharesOrPrincipalAmountType` | str / list[str] | Filter by type ('SH' or 'PRN') |
| `investmentDiscretion` | str / list[str] | Filter by discretion type |
| `putCall` | str / list[str] | Filter by put/call indicator |
| `otherManager` | str / list[str] | Exact match on other manager |
| `otherManagerPattern` | str | LIKE match on other manager |
| `votingAuthoritySole` | int / list[int] / tuple(int, int) | Sole voting shares or range |
| `votingAuthorityShared` | int / list[int] / tuple(int, int) | Shared voting shares or range |
| `votingAuthorityNone` | int / list[int] / tuple(int, int) | No voting shares or range |
| `hasValue` | bool | Filter by value presence |
| `hasShares` | bool | Filter by shares presence |
| `hasPutCall` | bool | Filter by put/call presence |
| `hasOtherManager` | bool | Filter by other manager presence |
| `hasVotingSole` | bool | Filter by sole voting authority presence |
| `hasVotingShared` | bool | Filter by shared voting authority presence |
| `hasVotingNone` | bool | Filter by no voting authority presence |
| `returnCols` | list[str] | Columns to return (default: all) |
| `page` | int | Page number (default: 1) |
| `pageSize` | int | Records per page (max: 25000) |

### Proxy Voting Records

Proxy voting records from institutional investors showing how they voted on corporate proposals.

```python
sheet.get_table('proxy-voting-records',
    accessionNumber=1234567890,
    cusip='037833100',
    meetingDate=('2024-01-01', '2024-12-31'),
    howVoted='For')
```

#### Schema

**Database:** `proxy_voting_records`  
**Table:** `proxy_voting_records_table`

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT UNSIGNED | Auto-increment primary key |
| `accessionNumber` | BIGINT UNSIGNED | SEC filing accession number |
| `cusip` | CHAR(9) | Security CUSIP identifier |
| `issuerName` | VARCHAR(256) | Name of the issuer |
| `meetingDate` | DATE | Date of shareholder meeting |
| `categoryType` | VARCHAR(256) | Category of vote (e.g., 'Director Election') |
| `voteDescription` | VARCHAR(8192) | Description of the proposal |
| `managementRecommendation` | VARCHAR(16) | Management's recommendation |
| `howVoted` | VARCHAR(16) | How the fund voted (e.g., 'For', 'Against') |
| `sharesVoted` | BIGINT UNSIGNED | Number of shares voted |
| `sharesOnLoan` | BIGINT UNSIGNED | Number of shares on loan |

**Indexes:**
- PRIMARY KEY: `(id, accessionNumber)`
- `idx_accession`, `idx_cusip`, `idx_meeting_date`, `idx_cusip_date`

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `accessionNumber` | int / list[int] | Filter by accession number(s) |
| `cusip` | str / list[str] | Filter by CUSIP |
| `issuerName` | str / list[str] | Exact match on issuer name |
| `issuerNamePattern` | str | LIKE match on issuer name |
| `meetingDate` | str / list[str] / tuple(str, str) | Meeting date(s) or range |
| `categoryType` | str / list[str] | Exact match on category |
| `categoryTypePattern` | str | LIKE match on category |
| `voteDescriptionPattern` | str | LIKE match on vote description |
| `managementRecommendation` | str / list[str] | Filter by management recommendation |
| `howVoted` | str / list[str] | Filter by vote choice |
| `sharesVoted` | int / list[int] / tuple(int, int) | Shares voted or range |
| `sharesOnLoan` | int / list[int] / tuple(int, int) | Shares on loan or range |
| `hasSharesVoted` | bool | Filter by shares voted presence |
| `hasSharesOnLoan` | bool | Filter by shares on loan presence |
| `returnCols` | list[str] | Columns to return (default: all) |
| `page` | int | Page number (default: 1) |
| `pageSize` | int | Records per page (max: 25000) |

### Insider Transactions

Insider trading data from Forms 3, 4, and 5 showing transactions and holdings by company insiders.

```python
sheet.get_table('insider-transactions',
    table='non-derivative-transaction',
    accessionNumber=1234567890,
    transactionCode='P',
    transactionDate=('2024-01-01', '2024-12-31'))
```

#### Schema

**Database:** `insider_transactions`

The insider transactions database contains 7 related tables. Use the `table` parameter to specify which table to query.

##### metadata_ownership_table

Filing-level metadata for ownership reports.

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT UNSIGNED | Auto-increment primary key |
| `accessionNumber` | BIGINT UNSIGNED | SEC filing accession number |
| `issuerCik` | BIGINT UNSIGNED | Issuer company CIK |
| `issuerName` | VARCHAR(128) | Issuer company name |
| `issuerTradingSymbol` | VARCHAR(16) | Issuer ticker symbol |
| `documentType` | VARCHAR(8) | Form type (3, 4, 5) |
| `periodOfReport` | DATE | Report period date |
| `notSubjectToSection16` | VARCHAR(8) | Section 16 exemption status |
| `form3HoldingsReported` | BIGINT UNSIGNED | Number of Form 3 holdings |
| `form4TransactionsReported` | BIGINT UNSIGNED | Number of Form 4 transactions |
| `dateOfOriginalSubmission` | DATE | Original submission date |
| `noSecuritiesOwned` | BIGINT UNSIGNED | No securities owned flag |
| `aff10b5One` | VARCHAR(8) | 10b5-1 plan indicator |
| `schemaVersion` | VARCHAR(8) | XML schema version |

**Indexes:** PRIMARY KEY `(id, accessionNumber)`, `idx_accession`

##### reporting_owner_ownership_table

Information about the reporting owner (insider).

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT UNSIGNED | Auto-increment primary key |
| `accessionNumber` | BIGINT UNSIGNED | SEC filing accession number |
| `rptOwnerCik` | BIGINT UNSIGNED | Reporting owner CIK |
| `rptOwnerName` | VARCHAR(256) | Reporting owner name |
| `rptOwnerStreet1` | VARCHAR(64) | Address line 1 |
| `rptOwnerStreet2` | VARCHAR(64) | Address line 2 |
| `rptOwnerCity` | VARCHAR(64) | City |
| `rptOwnerState` | CHAR(4) | State code |
| `rptOwnerStateDescription` | VARCHAR(64) | State name |
| `rptOwnerZipCode` | VARCHAR(16) | ZIP code |
| `rptOwnerIsDirector` | VARCHAR(8) | Is director flag |
| `rptOwnerIsOfficer` | VARCHAR(8) | Is officer flag |
| `rptOwnerIsTenPercentOwner` | VARCHAR(8) | Is 10% owner flag |
| `rptOwnerIsOther` | VARCHAR(8) | Other relationship flag |
| `rptOwnerOfficerTitle` | VARCHAR(64) | Officer title |
| `rptOwnerOtherText` | VARCHAR(64) | Other relationship text |

**Indexes:** PRIMARY KEY `(id, accessionNumber)`, `idx_accession`

##### non_derivative_transaction_ownership_table

Non-derivative security transactions (common stock, etc.).

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT UNSIGNED | Auto-increment primary key |
| `accessionNumber` | BIGINT UNSIGNED | SEC filing accession number |
| `securityTitle` | VARCHAR(128) | Security name |
| `transactionDate` | DATE | Transaction date |
| `deemedExecutionDate` | DATE | Deemed execution date |
| `transactionFormType` | BIGINT UNSIGNED | Form type |
| `transactionCode` | CHAR(1) | Transaction code (P, S, A, D, etc.) |
| `equitySwapInvolved` | VARCHAR(8) | Equity swap indicator |
| `transactionShares` | BIGINT UNSIGNED | Number of shares |
| `transactionPricePerShare` | BIGINT UNSIGNED | Price per share |
| `transactionAcquiredDisposedCode` | CHAR(1) | Acquired (A) or Disposed (D) |
| `sharesOwnedFollowingTransaction` | BIGINT UNSIGNED | Shares owned after |
| `valueOwnedFollowingTransaction` | BIGINT UNSIGNED | Value owned after |
| `directOrIndirectOwnership` | CHAR(1) | Direct (D) or Indirect (I) |
| `natureOfOwnership` | VARCHAR(256) | Nature of indirect ownership |
| `transactionTimeliness` | CHAR(1) | Timely or late filing |

**Indexes:** PRIMARY KEY `(id, accessionNumber)`, `idx_accession`

##### non_derivative_holding_ownership_table

Non-derivative security holdings (no transactions).

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT UNSIGNED | Auto-increment primary key |
| `accessionNumber` | BIGINT UNSIGNED | SEC filing accession number |
| `securityTitle` | VARCHAR(128) | Security name |
| `sharesOwnedFollowingTransaction` | BIGINT UNSIGNED | Shares owned |
| `valueOwnedFollowingTransaction` | BIGINT UNSIGNED | Value owned |
| `directOrIndirectOwnership` | CHAR(1) | Direct (D) or Indirect (I) |
| `natureOfOwnership` | VARCHAR(256) | Nature of indirect ownership |
| `transactionFormType` | BIGINT UNSIGNED | Form type |

**Indexes:** PRIMARY KEY `(id, accessionNumber)`, `idx_accession`

##### derivative_transaction_ownership_table

Derivative security transactions (options, warrants, etc.).

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT UNSIGNED | Auto-increment primary key |
| `accessionNumber` | BIGINT UNSIGNED | SEC filing accession number |
| `securityTitle` | VARCHAR(128) | Derivative security name |
| `conversionOrExercisePrice` | BIGINT UNSIGNED | Conversion/exercise price |
| `transactionDate` | DATE | Transaction date |
| `deemedExecutionDate` | DATE | Deemed execution date |
| `transactionFormType` | BIGINT UNSIGNED | Form type |
| `transactionCode` | CHAR(1) | Transaction code |
| `equitySwapInvolved` | VARCHAR(8) | Equity swap indicator |
| `transactionShares` | BIGINT UNSIGNED | Number of derivative securities |
| `transactionPricePerShare` | BIGINT UNSIGNED | Price per derivative |
| `transactionAcquiredDisposedCode` | CHAR(1) | Acquired (A) or Disposed (D) |
| `transactionTotalValue` | BIGINT UNSIGNED | Total transaction value |
| `exerciseDate` | DATE | Exercise date |
| `expirationDate` | DATE | Expiration date |
| `underlyingSecurityTitle` | VARCHAR(128) | Underlying security name |
| `underlyingSecurityShares` | BIGINT UNSIGNED | Underlying shares |
| `underlyingSecurityValue` | BIGINT UNSIGNED | Underlying value |
| `sharesOwnedFollowingTransaction` | BIGINT UNSIGNED | Derivatives owned after |
| `valueOwnedFollowingTransaction` | BIGINT UNSIGNED | Value owned after |
| `directOrIndirectOwnership` | CHAR(1) | Direct (D) or Indirect (I) |
| `natureOfOwnership` | VARCHAR(256) | Nature of indirect ownership |
| `transactionTimeliness` | CHAR(1) | Timely or late filing |

**Indexes:** PRIMARY KEY `(id, accessionNumber)`, `idx_accession`

##### derivative_holding_ownership_table

Derivative security holdings (no transactions).

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT UNSIGNED | Auto-increment primary key |
| `accessionNumber` | BIGINT UNSIGNED | SEC filing accession number |
| `securityTitle` | VARCHAR(128) | Derivative security name |
| `conversionOrExercisePrice` | BIGINT UNSIGNED | Conversion/exercise price |
| `exerciseDate` | DATE | Exercise date |
| `expirationDate` | DATE | Expiration date |
| `underlyingSecurityTitle` | VARCHAR(128) | Underlying security name |
| `underlyingSecurityShares` | BIGINT UNSIGNED | Underlying shares |
| `underlyingSecurityValue` | BIGINT UNSIGNED | Underlying value |
| `sharesOwnedFollowingTransaction` | BIGINT UNSIGNED | Derivatives owned |
| `valueOwnedFollowingTransaction` | BIGINT UNSIGNED | Value owned |
| `directOrIndirectOwnership` | CHAR(1) | Direct (D) or Indirect (I) |
| `natureOfOwnership` | VARCHAR(256) | Nature of indirect ownership |
| `transactionFormType` | BIGINT UNSIGNED | Form type |

**Indexes:** PRIMARY KEY `(id, accessionNumber)`, `idx_accession`

##### owner_signature_ownership_table

Signature information for the filing.

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT UNSIGNED | Auto-increment primary key |
| `accessionNumber` | BIGINT UNSIGNED | SEC filing accession number |
| `signatureName` | VARCHAR(256) | Name of signatory |
| `signatureDate` | DATE | Signature date |

**Indexes:** PRIMARY KEY `(id, accessionNumber)`, `idx_accession`

#### Parameters

##### Required Parameter

| Parameter | Type | Description |
|-----------|------|-------------|
| `table` | str | **Required.** Table to query: 'metadata', 'reporting-owner', 'non-derivative-transaction', 'non-derivative-holding', 'derivative-transaction', 'derivative-holding', or 'signature' |

##### Common Parameters (Available for All Tables)

| Parameter | Type | Description |
|-----------|------|-------------|
| `accessionNumber` | int / list[int] | Filter by accession number(s) |
| `returnCols` | list[str] | Columns to return (default: all) |
| `page` | int | Page number (default: 1) |
| `pageSize` | int | Records per page (max: 25000) |

##### Metadata Table Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `issuerCik` | int / list[int] | Filter by issuer CIK |
| `issuerName` | str / list[str] | Exact match on issuer name |
| `issuerNamePattern` | str | LIKE match on issuer name |
| `issuerTradingSymbol` | str / list[str] | Filter by ticker symbol |
| `documentType` | str / list[str] | Filter by form type |
| `periodOfReport` | str / list[str] / tuple(str, str) | Period of report date(s) or range |
| `dateOfOriginalSubmission` | str / list[str] / tuple(str, str) | Submission date(s) or range |
| `notSubjectToSection16` | str / list[str] | Section 16 exemption values |
| `form3HoldingsReported` | int / list[int] / tuple(int, int) | Form 3 holdings count or range |
| `form4TransactionsReported` | int / list[int] / tuple(int, int) | Form 4 transactions count or range |
| `noSecuritiesOwned` | int / list[int] / tuple(int, int) | No securities flag or range |
| `aff10b5One` | str / list[str] | 10b5-1 plan values |
| `schemaVersion` | str / list[str] | Schema version |
| `hasForm3Holdings` | bool | Filter by Form 3 holdings presence |
| `hasForm4Transactions` | bool | Filter by Form 4 transactions presence |
| `hasNoSecurities` | bool | Filter by no securities flag |

##### Reporting Owner Table Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `rptOwnerCik` | int / list[int] | Filter by reporting owner CIK |
| `rptOwnerName` | str / list[str] | Exact match on owner name |
| `rptOwnerNamePattern` | str | LIKE match on owner name |
| `rptOwnerCity` | str / list[str] | Exact match on city |
| `rptOwnerCityPattern` | str | LIKE match on city |
| `rptOwnerState` | str / list[str] | Filter by state code |
| `rptOwnerStateDescription` | str / list[str] | Exact match on state name |
| `rptOwnerStateDescriptionPattern` | str | LIKE match on state name |
| `rptOwnerStreet1Pattern` | str | LIKE match on street 1 |
| `rptOwnerStreet2Pattern` | str | LIKE match on street 2 |
| `rptOwnerZipCode` | str / list[str] | Filter by ZIP code |
| `rptOwnerIsDirector` | str / list[str] | Director flag values |
| `rptOwnerIsOfficer` | str / list[str] | Officer flag values |
| `rptOwnerIsTenPercentOwner` | str / list[str] | 10% owner flag values |
| `rptOwnerIsOther` | str / list[str] | Other flag values |
| `rptOwnerOfficerTitle` | str / list[str] | Exact match on officer title |
| `rptOwnerOfficerTitlePattern` | str | LIKE match on officer title |
| `rptOwnerOtherText` | str / list[str] | Exact match on other text |
| `rptOwnerOtherTextPattern` | str | LIKE match on other text |
| `isDirector` | bool | Filter for directors |
| `isOfficer` | bool | Filter for officers |
| `isTenPercentOwner` | bool | Filter for 10% owners |
| `isOther` | bool | Filter for other relationships |

##### Non-Derivative Transaction Table Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `securityTitle` | str / list[str] | Exact match on security name |
| `securityTitlePattern` | str | LIKE match on security name |
| `transactionDate` | str / list[str] / tuple(str, str) | Transaction date(s) or range |
| `deemedExecutionDate` | str / list[str] / tuple(str, str) | Deemed execution date(s) or range |
| `transactionFormType` | int / list[int] | Filter by form type |
| `transactionCode` | str / list[str] | Transaction code(s) |
| `equitySwapInvolved` | str / list[str] | Equity swap values |
| `transactionShares` | int / list[int] / tuple(int, int) | Transaction shares or range |
| `transactionPricePerShare` | int / list[int] / tuple(int, int) | Price per share or range |
| `transactionAcquiredDisposedCode` | str / list[str] | Acquired/Disposed code |
| `sharesOwnedFollowingTransaction` | int / list[int] / tuple(int, int) | Shares owned after or range |
| `valueOwnedFollowingTransaction` | int / list[int] / tuple(int, int) | Value owned after or range |
| `directOrIndirectOwnership` | str / list[str] | Direct/Indirect code |
| `natureOfOwnership` | str / list[str] | Exact match on ownership nature |
| `natureOfOwnershipPattern` | str | LIKE match on ownership nature |
| `transactionTimeliness` | str / list[str] | Timeliness code |
| `hasTransactionShares` | bool | Filter by transaction shares presence |
| `hasTransactionPrice` | bool | Filter by price presence |
| `isAcquisition` | bool | Filter for acquisitions (code 'A') |
| `isDisposal` | bool | Filter for disposals (code 'D') |

##### Non-Derivative Holding Table Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `securityTitle` | str / list[str] | Exact match on security name |
| `securityTitlePattern` | str | LIKE match on security name |
| `sharesOwnedFollowingTransaction` | int / list[int] / tuple(int, int) | Shares owned or range |
| `valueOwnedFollowingTransaction` | int / list[int] / tuple(int, int) | Value owned or range |
| `directOrIndirectOwnership` | str / list[str] | Direct/Indirect code |
| `natureOfOwnership` | str / list[str] | Exact match on ownership nature |
| `natureOfOwnershipPattern` | str | LIKE match on ownership nature |
| `transactionFormType` | int / list[int] | Filter by form type |

##### Derivative Transaction Table Parameters

Includes all Non-Derivative Transaction parameters plus:

| Parameter | Type | Description |
|-----------|------|-------------|
| `conversionOrExercisePrice` | int / list[int] / tuple(int, int) | Conversion/exercise price or range |
| `transactionTotalValue` | int / list[int] / tuple(int, int) | Total value or range |
| `exerciseDate` | str / list[str] / tuple(str, str) | Exercise date(s) or range |
| `expirationDate` | str / list[str] / tuple(str, str) | Expiration date(s) or range |
| `underlyingSecurityTitle` | str / list[str] | Exact match on underlying security |
| `underlyingSecurityTitlePattern` | str | LIKE match on underlying security |
| `underlyingSecurityShares` | int / list[int] / tuple(int, int) | Underlying shares or range |
| `underlyingSecurityValue` | int / list[int] / tuple(int, int) | Underlying value or range |

##### Derivative Holding Table Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `securityTitle` | str / list[str] | Exact match on security name |
| `securityTitlePattern` | str | LIKE match on security name |
| `conversionOrExercisePrice` | int / list[int] / tuple(int, int) | Conversion/exercise price or range |
| `exerciseDate` | str / list[str] / tuple(str, str) | Exercise date(s) or range |
| `expirationDate` | str / list[str] / tuple(str, str) | Expiration date(s) or range |
| `underlyingSecurityTitle` | str / list[str] | Exact match on underlying security |
| `underlyingSecurityTitlePattern` | str | LIKE match on underlying security |
| `underlyingSecurityShares` | int / list[int] / tuple(int, int) | Underlying shares or range |
| `underlyingSecurityValue` | int / list[int] / tuple(int, int) | Underlying value or range |
| `sharesOwnedFollowingTransaction` | int / list[int] / tuple(int, int) | Shares owned or range |
| `valueOwnedFollowingTransaction` | int / list[int] / tuple(int, int) | Value owned or range |
| `directOrIndirectOwnership` | str / list[str] | Direct/Indirect code |
| `natureOfOwnership` | str / list[str] | Exact match on ownership nature |
| `natureOfOwnershipPattern` | str | LIKE match on ownership nature |
| `transactionFormType` | int / list[int] | Filter by form type |

##### Signature Table Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `signatureName` | str / list[str] | Exact match on signature name |
| `signatureNamePattern` | str | LIKE match on signature name |
| `signatureDate` | str / list[str] / tuple(str, str) | Signature date(s) or range |
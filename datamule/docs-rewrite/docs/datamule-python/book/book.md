# Book

Book is a class for interacting with datamule's S3 Layer.


## `download_dataset`

Download pre-built datasets directly from Datamule.

Available datasets:

- **sec_accessions**: SEC Accessions Master Index - newline-delimited text file of all accession numbers

- **sec_master_submissions**: SEC Master Submissions Table - comprehensive master index with filing metadata
  - Columns: cik (Int64), accessionNumber (String), filingDate (Date), submissionType (String), reportDate (Date), acceptanceDateTime (Datetime), act (String), fileNumber (String), filmNumber (String), items (String), size (Int64), isXBRL (Boolean), isInlineXBRL (Boolean)

- **sec_accession_cik_table**: SEC Accession CIK Table - links accession numbers to company CIKs
  - Columns: accessionNumber (BIGINT UNSIGNED), cik (BIGINT UNSIGNED)

- **sec_documents_table**: SEC Documents Table - document-level details for all files within filings
  - Columns: accessionNumber (BIGINT UNSIGNED), documentType (VARCHAR(128)), sequence (SMALLINT), filename (VARCHAR(500)), description (VARCHAR(1000)), secsgmlSizeBytes (INT)

- **sec_submission_details_table**: SEC Submissions Details Table - filing metadata with submission types and dates
  - Columns: accessionNumber (BIGINT UNSIGNED), submissionType (VARCHAR(16)), filingDate (DATE), reportDate (DATE), detectedTime (DATETIME), containsXBRL (BOOLEAN)

- **simple_xbrl_table**: Simple XBRL Table - parsed XBRL facts from SEC filings
  - Columns: id (BIGINT UNSIGNED), accessionNumber (BIGINT UNSIGNED), context_id (BIGINT UNSIGNED), taxonomy (VARCHAR(16)), name (VARCHAR(256)), value (TEXT), period_start_date (DATE), period_end_date (DATE), members (TEXT)

- **proxy_voting_records_table**: Proxy Voting Records Table - institutional investor voting records
  - Columns: id (BIGINT UNSIGNED), accessionNumber (BIGINT UNSIGNED), cusip (CHAR(9)), issuerName (VARCHAR(256)), meetingDate (DATE), categoryType (VARCHAR(256)), voteDescription (VARCHAR(8192)), managementRecommendation (VARCHAR(16)), howVoted (VARCHAR(16)), sharesVoted (BIGINT UNSIGNED), sharesOnLoan (BIGINT UNSIGNED)

- **institutional_holdings_table**: Institutional Holdings Table - 13F institutional holdings
  - Columns: id (BIGINT UNSIGNED), accessionNumber (BIGINT UNSIGNED), cusip (CHAR(9)), nameOfIssuer (VARCHAR(256)), titleOfClass (VARCHAR(256)), value (BIGINT UNSIGNED), sharesOrPrincipalAmount (BIGINT UNSIGNED), sharesOrPrincipalAmountType (VARCHAR(16)), investmentDiscretion (VARCHAR(16)), putCall (VARCHAR(16)), otherManager (VARCHAR(256)), votingAuthoritySole (BIGINT UNSIGNED), votingAuthorityShared (BIGINT UNSIGNED), votingAuthorityNone (BIGINT UNSIGNED)

- **metadata_ownership_table**: Insider Ownership Metadata Table - filing-level metadata for insider reports
  - Columns: id (BIGINT UNSIGNED), accessionNumber (BIGINT UNSIGNED), issuerCik (BIGINT UNSIGNED), issuerName (VARCHAR(128)), issuerTradingSymbol (VARCHAR(16)), documentType (VARCHAR(8)), periodOfReport (DATE), notSubjectToSection16 (VARCHAR(8)), form3HoldingsReported (BIGINT UNSIGNED), form4TransactionsReported (BIGINT UNSIGNED), dateOfOriginalSubmission (DATE), noSecuritiesOwned (BIGINT UNSIGNED), aff10b5One (VARCHAR(8)), schemaVersion (VARCHAR(8))

- **reporting_owner_ownership_table**: Insider Reporting Owner Table - insider details and relationships
  - Columns: id (BIGINT UNSIGNED), accessionNumber (BIGINT UNSIGNED), rptOwnerCik (BIGINT UNSIGNED), rptOwnerName (VARCHAR(256)), rptOwnerStreet1 (VARCHAR(64)), rptOwnerStreet2 (VARCHAR(64)), rptOwnerCity (VARCHAR(64)), rptOwnerState (CHAR(4)), rptOwnerStateDescription (VARCHAR(64)), rptOwnerZipCode (VARCHAR(16)), rptOwnerIsDirector (VARCHAR(8)), rptOwnerIsOfficer (VARCHAR(8)), rptOwnerIsTenPercentOwner (VARCHAR(8)), rptOwnerIsOther (VARCHAR(8)), rptOwnerOfficerTitle (VARCHAR(64)), rptOwnerOtherText (VARCHAR(64))

- **non_derivative_transaction_ownership_table**: Insider Non-Derivative Transactions Table - common stock transactions
  - Columns: id (BIGINT UNSIGNED), accessionNumber (BIGINT UNSIGNED), securityTitle (VARCHAR(128)), transactionDate (DATE), deemedExecutionDate (DATE), transactionFormType (BIGINT UNSIGNED), transactionCode (CHAR(1)), equitySwapInvolved (VARCHAR(8)), transactionShares (BIGINT UNSIGNED), transactionPricePerShare (BIGINT UNSIGNED), transactionAcquiredDisposedCode (CHAR(1)), sharesOwnedFollowingTransaction (BIGINT UNSIGNED), valueOwnedFollowingTransaction (BIGINT UNSIGNED), directOrIndirectOwnership (CHAR(1)), natureOfOwnership (VARCHAR(256)), transactionTimeliness (CHAR(1))

- **non_derivative_holding_ownership_table**: Insider Non-Derivative Holdings Table - current ownership positions
  - Columns: id (BIGINT UNSIGNED), accessionNumber (BIGINT UNSIGNED), securityTitle (VARCHAR(128)), sharesOwnedFollowingTransaction (BIGINT UNSIGNED), valueOwnedFollowingTransaction (BIGINT UNSIGNED), directOrIndirectOwnership (CHAR(1)), natureOfOwnership (VARCHAR(256)), transactionFormType (BIGINT UNSIGNED)

- **derivative_transaction_ownership_table**: Insider Derivative Transactions Table - options, warrants transactions
  - Columns: id (BIGINT UNSIGNED), accessionNumber (BIGINT UNSIGNED), securityTitle (VARCHAR(128)), conversionOrExercisePrice (BIGINT UNSIGNED), transactionDate (DATE), deemedExecutionDate (DATE), transactionFormType (BIGINT UNSIGNED), transactionCode (CHAR(1)), equitySwapInvolved (VARCHAR(8)), transactionShares (BIGINT UNSIGNED), transactionPricePerShare (BIGINT UNSIGNED), transactionAcquiredDisposedCode (CHAR(1)), transactionTotalValue (BIGINT UNSIGNED), exerciseDate (DATE), expirationDate (DATE), underlyingSecurityTitle (VARCHAR(128)), underlyingSecurityShares (BIGINT UNSIGNED), underlyingSecurityValue (BIGINT UNSIGNED), sharesOwnedFollowingTransaction (BIGINT UNSIGNED), valueOwnedFollowingTransaction (BIGINT UNSIGNED), directOrIndirectOwnership (CHAR(1)), natureOfOwnership (VARCHAR(256)), transactionTimeliness (CHAR(1))

- **derivative_holding_ownership_table**: Insider Derivative Holdings Table - derivative security positions
  - Columns: id (BIGINT UNSIGNED), accessionNumber (BIGINT UNSIGNED), securityTitle (VARCHAR(128)), conversionOrExercisePrice (BIGINT UNSIGNED), exerciseDate (DATE), expirationDate (DATE), underlyingSecurityTitle (VARCHAR(128)), underlyingSecurityShares (BIGINT UNSIGNED), underlyingSecurityValue (BIGINT UNSIGNED), sharesOwnedFollowingTransaction (BIGINT UNSIGNED), valueOwnedFollowingTransaction (BIGINT UNSIGNED), directOrIndirectOwnership (CHAR(1)), natureOfOwnership (VARCHAR(256)), transactionFormType (BIGINT UNSIGNED)

- **owner_signature_ownership_table**: Insider Owner Signatures Table - signature information for filings
  - Columns: id (BIGINT UNSIGNED), accessionNumber (BIGINT UNSIGNED), signatureName (VARCHAR(256)), signatureDate (DATE)

### Example

Download a dataset with auto-detected filename:
```python
from datamule import Book
book = Book()

book.download_dataset(
    dataset='sec_accessions',
    api_key = None # Uses environmental variable if set
)
```

Download with custom filename:
```python
book.download_dataset(
    dataset='institutional_holdings_table',
    filename='my_holdings_data.parquet'
)
```

### Parameters

- **dataset**: Dataset identifier (lowercase underscore format, e.g. 'sec_accessions')
- **api_key**: Your Datamule API key
- **filename**: Optional output filename. If not provided, extracts filename from download URL with correct extension


## `s3_transfer`

Transfer from datamule S3 to your S3 bucket.

Supported buckets:

- **filings_sgml_r2**: Every SEC submission in .sgml or .sgml.zst form. Type is included in metadata.

Supported providers:

- AWS

Easy to add more providers, if you have a preferred one please submit it [here](https://github.com/john-friedman/datamule-python/issues).

Note: If run locally from residential internet, this will likely be slow. Run in the cloud or on corporate internet.

### Example

Transfer to your S3
```python
from datamule import Book
import os


# Good practice to not hardcode your api keys
s3_credentials = {'s3_provider':'aws', # S3 Provider
                    'aws_access_key_id':os.environ['AWS_ACCESS_KEY_ID'],
                    'aws_secret_access_key':os.environ['AWS_SECRET_ACCESS_KEY'],
                    'region_name':'us-east-1', # Example region
                    'bucket_name':'mybucket'} # Your bucket name.


book = Book()

book.s3_transfer(datamule_bucket='filings_sgml_r2',s3_credentials=s3_credentials,force_daily=True,filing_date=('2025-09-03','2025-09-11'),
                 max_workers=128,errors_json_filename='s3_transfer_errors.json',retry_errors=3)
```

Fill in missing from errors.json.
```python
book.s3_transfer(datamule_bucket='filings_sgml_r2',s3_credentials=s3_credentials,accession=['000000000025002258'],
                 max_workers=128)
```

### Parameters

- datamule_bucket: which datamule s3 bucket you want to transfer from.
- s3_credentials: dictionary of your bucket's credentials.
- force_daily: when set to True, constructs index of urls for one day, then transfers, and repeats. Otherwise, constructs index all at once.
- filing_date: subset by date. Supports start and end date tuple, list or string.
- submission_type: subset, e.g. by 10-K, or ['3','4','5'].
- datamule_api_key: If you have DATAMULE_API_KEY set to your environment it will be auto detected. This is for legacy purposes.
- retry_errors: How many times to retry a file in the transfer.
- errors_json_filename: filename of errors.
- max_workers: change depending on your machine to increase speed of transfers.
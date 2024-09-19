# Edgar Submissions

[Endpoint](https://data.sec.gov/submissions/CIK0001318605.json)
[Archive Endpoint](https://data.sec.gov/submissions/CIK0001318605-submissions-001.json) - only contains `filings` keys
## Response

- `cik`: Central Index Key of the entity.
- `entityType`: Type of the entity (e.g., "operating").
- `sic`: Standard Industrial Classification code.
- `sicDescription`: Description of the SIC code.
- `ownerOrg`: Owner organization category.
- `insiderTransactionForOwnerExists`: Flag indicating if insider transactions for owner exist (0 or 1).
- `insiderTransactionForIssuerExists`: Flag indicating if insider transactions for issuer exist (0 or 1).
- `name`: Name of the entity.
- `tickers`: Array of stock ticker symbols.
- `exchanges`: Array of stock exchanges where the entity is listed.
- `ein`: Employer Identification Number.
- `description`: Description of the entity.
- `website`: Entity's website URL.
- `investorWebsite`: Entity's investor relations website URL.
- `category`: SEC filer category.
- `fiscalYearEnd`: Fiscal year end date in MMDD format.
- `stateOfIncorporation`: State of incorporation code.
- `stateOfIncorporationDescription`: Full name of the state of incorporation.
- `addresses`: Object containing mailing and business addresses:
  - `mailing`: Mailing address details.
  - `business`: Business address details.
    Each address contains:
    - `street1`: First line of the street address.
    - `street2`: Second line of the street address (if applicable).
    - `city`: City name.
    - `stateOrCountry`: State or country code.
    - `zipCode`: ZIP or postal code.
    - `stateOrCountryDescription`: Full name of the state or country.
- `phone`: Contact phone number.
- `flags`: Any relevant flags for the entity.
- `formerNames`: Array of objects containing information about previous names:
  - `name`: Previous name of the entity.
  - `from`: Start date of the name use (ISO 8601 format).
  - `to`: End date of the name use (ISO 8601 format).
- `filings`: Object containing recent filings information:
  - `recent`: Object with arrays of recent filing details:
    - `accessionNumber`: Array of accession numbers.
    - `filingDate`: Array of filing dates.
    - `reportDate`: Array of report dates.
    - `acceptanceDateTime`: Array of acceptance date and times.
    - `act`: Array of acts under which filings were made.
    - `form`: Array of form types.
    - `fileNumber`: Array of file numbers.
    - `filmNumber`: Array of film numbers.
    - `items`: Array of items (e.g., "2.02,9.01").
    - `size`: Array of file sizes.
    - `isXBRL`: Array of flags indicating XBRL format (0 or 1).
    - `isInlineXBRL`: Array of flags indicating inline XBRL format (0 or 1).
    - `primaryDocument`: Array of primary document filenames.
    - `primaryDocDescription`: Array of primary document descriptions.
- `files`: Array of objects containing information about submission files:
    - `name`: Name of the submissions file.
    - `filingCount`: Number of filings in the file.
    - `filingFrom`: Start date of filings in the file.
    - `filingTo`: End date of filings in the file.
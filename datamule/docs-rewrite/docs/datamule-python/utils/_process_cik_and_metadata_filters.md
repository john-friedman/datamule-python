# _process_cik_and_metadata_filters

`_process_cik_and_metadata_filters` is a function that takes parameters such as `ticker` or `sic` and returns all CIKs which match using `.datamule\listed_filer_metadata.csv`.


## Parameters
- `cik` - CIK number(s)
- `ticker` - Stock ticker symbol(s)
- `sic` - Standard Industrial Classification code(s)
- `state` - State(s) of incorporation
- `category` - Filer category
- `industry` - Industry description
- `exchange` - Stock exchange(s)
- `name` - Company name
- `business_city` - City of business
- `business_stateOrCountry` - State/country of business
- `ein` - Employer Identification Number
- `entityType` - Entity type
- `fiscalYearEnd` - Fiscal year end date
- `insiderTransactionForIssuerExists` - Insider transaction flag
- `insiderTransactionForOwnerExists` - Owner transaction flag
- `mailing_city` - Mailing address city
- `mailing_stateOrCountry` - Mailing address state/country
- `ownerOrg` - Owner organization
- `phone` - Phone number
- `sicDescription` - SIC description
- `stateOfIncorporationDescription` - State of incorporation description
- `tickers` - List of ticker symbols
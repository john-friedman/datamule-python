# Sheet

???+ warning "Rewrite Coming"
    This code will be rewritten soon as part of an update that allows conversion of all SEC xml files into tabular form.

???+ warning "Data last updated in mid april 2025"
    This will be changed soon

Sheet is a class that allows you to download and work with tabular datasets from the SEC (Securities and Exchange Commission).

## Functions

### XBRL Data

#### `download_xbrl(cik=None, ticker=None, **kwargs)`
Retrieves XBRL data for companies and saves it to disk.

If `cik` and `ticker` are not provided, data for all companies with tickers will be downloaded.
The data is saved to the directory specified when initializing the Sheet.

**Parameters:**
- `cik`: Central Index Key identifier(s) for the company(ies) (str, int, list, or None)
- `ticker`: Stock ticker symbol(s) (str, list, or None)
- `**kwargs`: Additional search criteria including name, entityType, sic, sicDescription, ownerOrg, insiderTransactionForOwnerExists, insiderTransactionForIssuerExists, exchanges, ein, description, website, investorWebsite, category, fiscalYearEnd, stateOfIncorporation, stateOfIncorporationDescription, phone, flags, various address fields (mailing and business)

**Example:**

```python
# Download XBRL data for Tesla
sheet.download_xbrl(ticker="TSLA")

# Download XBRL data for multiple companies by CIK
sheet.download_xbrl(cik=["1318605", "320193"])  # Tesla and Apple
```

### Form 13F-HR Information Table

#### Get Data

##### `get_information_table(columns=None, ..., api_key=None, print_cost=True, verbose=False)`
Query the SEC BigQuery API for 13F-HR information table data (institutional holdings).

**Parameters:**
- `columns`: Specific columns to return (List[str], optional)
- `name_of_issuer`: Name of the issuing company (string, list, or None)
- `title_of_class`: Class of securities (string, list, or None)
- `cusip`: CUSIP identifier (string, list, or None)
- `value`: Value of holdings in $ (numeric, tuple for range, or None)
- `ssh_prnamt`: Number of shares held (numeric, tuple for range, or None)
- `ssh_prnamt_type`: Type of shares (e.g., SH for shares) (string, list, or None)
- `investment_discretion`: Level of investment discretion (string, list, or None)
- `voting_authority_sole`: Shares with sole voting authority (numeric, tuple for range, or None)
- `voting_authority_shared`: Shares with shared voting authority (numeric, tuple for range, or None)
- `voting_authority_none`: Shares with no voting authority (numeric, tuple for range, or None)
- `reporting_owner_cik`: CIK of the reporting owner (string, list, or None)
- `put_call`: Put or call indicator (string, list, or None)
- `other_manager`: Other managers reporting the security (string, list, or None)
- `figi`: Financial Instrument Global Identifier (string, list, or None)
- `accession`: SEC filing accession number (string, list, or None)
- `filing_date`: Date of filing (string, list, or tuple for date range)
- `api_key`: SEC BigQuery API key. If None, looks for DATAMULE_API_KEY env variable (string, optional)
- `print_cost`: Whether to print the query cost information (bool)
- `verbose`: Whether to print additional information about the query (bool)

**Return:** Records matching the query (List[Dict])

**Filter Format Options:**
* String filters: Exact match (e.g., `cusip="023135106"`)
* List filters: Match any in list (e.g., `name_of_issuer=["Apple Inc", "Microsoft Corp"]`)
* Numeric range filters: (min, max) tuple (e.g., `value=(1000000, 10000000)`)
* Date range filters: (start_date, end_date) tuple (e.g., `filing_date=("2023-01-01", "2023-12-31")`)

**Example:**

```python
# Get all BlackRock holdings of Apple stock
holdings = sheet.get_information_table(
    name_of_issuer="Apple Inc",
    reporting_owner_cik="1364742",  # BlackRock
    columns=["value", "ssh_prnamt", "filing_date"]
)
```

#### Download to CSV

##### `download_information_table(filepath, columns=None, ..., api_key=None, print_cost=True, verbose=False)`
Query the SEC BigQuery API for 13F-HR information table data and save to CSV.

**Parameters:**
- `filepath`: Path where to save the CSV file (str)
- `columns`: Specific columns to return (List[str], optional)
- [All other parameters same as `get_information_table`]

**Example:**

```python
# Download all Vanguard holdings to CSV
sheet.download_information_table(
    filepath="vanguard_holdings.csv",
    reporting_owner_cik="0000102909",  # Vanguard
    filing_date=("2023-01-01", "2023-12-31"),
    verbose=True
)
```

### Form 3, 4, 5 (Insider Transactions)

#### Get Data

##### `get_345(columns=None, ..., api_key=None, print_cost=True, verbose=False)`
Query the SEC BigQuery API for Form 3, 4, 5 insider transaction data.

**Parameters:**
- `columns`: Specific columns to return (List[str], optional)
- `is_derivative`: Whether transaction involves derivative securities (boolean)
- `is_non_derivative`: Whether transaction involves non-derivative securities (boolean)
- `security_title`: Title of security (string, list, or None)
- `transaction_date`: Date of transaction (string, list, or tuple for date range)
- `document_type`: Form type (3, 4, or 5) (string, list, or None)
- `transaction_code`: Transaction code (e.g., P for purchase, S for sale) (string, list, or None)
- `equity_swap_involved`: Whether equity swap was involved (boolean)
- `transaction_timeliness`: Timeliness of reporting (string, list, or None)
- `transaction_shares`: Number of shares in transaction (numeric, tuple for range, or None)
- `transaction_price_per_share`: Price per share (numeric, tuple for range, or None)
- `shares_owned_following_transaction`: Shares owned after transaction (numeric, tuple for range, or None)
- `ownership_type`: Type of ownership (D for direct, I for indirect) (string, list, or None)
- `deemed_execution_date`: Deemed execution date (string, list, or tuple for date range)
- `conversion_or_exercise_price`: Price for conversion or exercise (numeric, tuple for range, or None)
- `exercise_date`: Exercise date (string, list, or tuple for date range)
- `expiration_date`: Expiration date (string, list, or tuple for date range)
- `underlying_security_title`: Title of underlying security (string, list, or None)
- `underlying_security_shares`: Shares of underlying security (numeric, tuple for range, or None)
- `underlying_security_value`: Value of underlying security (numeric, tuple for range, or None)
- `accession`: SEC filing accession number (string, list, or None)
- `reporting_owner_cik`: CIK of the reporting insider (string, list, or None)
- `issuer_cik`: CIK of the company (string, list, or None)
- `filing_date`: Date of filing (string, list, or tuple for date range)
- `api_key`: SEC BigQuery API key. If None, looks for DATAMULE_API_KEY env variable (string, optional)
- `print_cost`: Whether to print the query cost information (bool)
- `verbose`: Whether to print additional information about the query (bool)

**Return:** Records matching the query (List[Dict])

**Example:**

```python
# Get all Elon Musk's Tesla transactions
transactions = sheet.get_345(
    reporting_owner_cik="1494730",  # Elon Musk's CIK
    issuer_cik="1318605",  # Tesla's CIK
    columns=["transaction_date", "transaction_code", "transaction_shares", 
             "transaction_price_per_share", "is_derivative"]
)
```

#### Download to CSV

##### `download_345(filepath, columns=None, ..., api_key=None, print_cost=True, verbose=False)`
Query the SEC BigQuery API for Form 3, 4, 5 insider transaction data and save to CSV.

**Parameters:**
- `filepath`: Path where to save the CSV file (str)
- `columns`: Specific columns to return (List[str], optional)
- [All other parameters same as `get_345`]

**Examples:**

```python
# Download all Tesla insider transactions for a year
sheet.download_345(
    filepath="tesla_insider_transactions.csv",
    issuer_cik="1318605",  # Tesla's CIK
    filing_date=("2023-01-01", "2023-12-31"),
    columns=["transaction_date", "security_title", "transaction_code", 
             "transaction_shares", "transaction_price_per_share", 
             "reporting_owner_cik", "is_derivative"],
    verbose=True
)

# Download all Elon Musk's transactions to CSV
sheet.download_345(
    filepath="elon_transactions.csv",
    reporting_owner_cik="1494730",  # Elon Musk's CIK
    verbose=True
)

# Get all large insider acquisitions (over 10,000 shares)
sheet.download_345(
    filepath="large_acquisitions.csv",
    transaction_code="A",  # Acquisition/grant
    shares_owned_following_transaction=(10000, None),  # Minimum of 10,000 shares
    is_derivative=False,  # Only non-derivative transactions
    verbose=True
)
```

### Form NPX (Proxy Voting Records)

#### Get Data

##### `get_proxy_voting_record(columns=None, ..., api_key=None, print_cost=True, verbose=False)`
Query the SEC BigQuery API for NPX proxy voting record data.

**Parameters:**
- `columns`: Specific columns to return (List[str], optional)
- `meeting_date`: Date of shareholder meeting (string, list, or tuple for date range)
- `isin`: International Securities Identification Number (string, list, or None)
- `cusip`: CUSIP identifier (string, list, or None)
- `issuer_name`: Name of the issuing company (string, list, or None)
- `vote_description`: Description of the vote (string, list, or None)
- `shares_on_loan`: Number of shares on loan (numeric, tuple for range, or None)
- `shares_voted`: Number of shares voted (numeric, tuple for range, or None)
- `vote_category`: Category of vote (string, list, or None)
- `vote_record`: Record of vote (string, list, or None)
- `vote_source`: Source of vote (string, list, or None)
- `how_voted`: How the vote was cast (e.g., FOR, AGAINST, ABSTAIN) (string, list, or None)
- `figi`: Financial Instrument Global Identifier (string, list, or None)
- `management_recommendation`: Management's recommendation for the vote (string, list, or None)
- `accession`: SEC filing accession number (string, list, or None)
- `reporting_owner_cik`: CIK of the reporting owner (string, list, or None)
- `filing_date`: Date of filing (string, list, or tuple for date range)
- `api_key`: SEC BigQuery API key. If None, looks for DATAMULE_API_KEY env variable (string, optional)
- `print_cost`: Whether to print the query cost information (bool)
- `verbose`: Whether to print additional information about the query (bool)

**Return:** Records matching the query (List[Dict])

**Filter Format Options:**
* String filters: Exact match (e.g., `cusip="037833100"`)
* List filters: Match any in list (e.g., `issuer_name=["Apple Inc", "Tesla, Inc"]`)
* Numeric range filters: (min, max) tuple (e.g., `shares_voted=(1000000, None)`)
* Date range filters: (start_date, end_date) tuple (e.g., `filing_date=("2023-01-01", "2023-12-31")`)

**Example:**

```python
# Get all BlackRock votes for Apple in 2023
votes = sheet.get_proxy_voting_record(
    issuer_name="Apple Inc",
    reporting_owner_cik="1364742",  # BlackRock
    meeting_date=("2023-01-01", "2023-12-31"),
    columns=["vote_description", "how_voted", "management_recommendation"]
)
```

#### Download to CSV

##### `download_proxy_voting_record(filepath, columns=None, ..., api_key=None, print_cost=True, verbose=False)`
Query the SEC BigQuery API for NPX proxy voting record data and save to CSV.

**Parameters:**
- `filepath`: Path where to save the CSV file (str)
- `columns`: Specific columns to return (List[str], optional)
- [All other parameters same as `get_proxy_voting_record`]

**Examples:**

```python
# Download recent proxy votes
sheet.download_proxy_voting_record(
    filepath="recent_proxy_votes.csv",
    filing_date=("2025-02-01", None),  # From February 2025 to present
    verbose=True
)

# Download Apple and Microsoft proxy votes
sheet.download_proxy_voting_record(
    filepath="apple_msft_votes.csv",
    cusip=["037833100", "594918104"],  # Apple and Microsoft CUSIPs
    columns=["meetingDate", "issuerName", "voteDescription", "howVoted", 
             "sharesVoted", "filingDate", "reportingOwnerCIK"]
)

# Download votes against management recommendations
sheet.download_proxy_voting_record(
    filepath="against_mgmt.csv",
    how_voted="AGAINST",
    management_recommendation="FOR"
)

# Download all proxy votes for Tesla
sheet.download_proxy_voting_record(
    filepath="tesla.csv",
    cusip="88160R101"  # Tesla's CUSIP
)
```

## Available Datasets

* **XBRL** (via SEC, free): Company financial data in XBRL format
* **Institutional Holdings** (via datamule, paid): Constructed from 13F-HR INFORMATION TABLE
* **Insider Transactions** (via datamule, paid): Constructed from Forms 3, 4, and 5
* **Proxy Voting Records** (via datamule, paid): Constructed from Form NPX
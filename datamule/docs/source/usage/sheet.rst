Sheet
=====

Sheet is a class that allows you to download tabular datasets.

..
    Sheet will have leaves in the future

Functions
---------

``download_xbrl(cik, **kwargs)``
    Retrieves the data and saves it to disk. if cik is not provided, all data will be downloaded.

``get_information_table(table_type="INFORMATION_TABLE", columns=None, ..., api_key=None, print_cost=True, verbose=False)``
    Query the Datamule BigQuery API for 13F-HR information table data and returns the results as a list of dictionaries.

``download_information_table(filepath, table_type="INFORMATION_TABLE", columns=None, ..., api_key=None, print_cost=True, verbose=False)``
    Query the Datamule BigQuery API for 13F-HR information table data and save the results directly to a CSV file at the specified filepath.

Shared Parameters
~~~~~~~~~~~~~~~~~

For download_xbrl:
^^^^^^^^^^^^^^^^^^

:param cik: Central Index Key identifier for the company
:param ticker: Stock ticker symbol
:param \**kwargs: Additional search criteria including name, entityType, sic, sicDescription, 
                ownerOrg, insiderTransactionForOwnerExists, insiderTransactionForIssuerExists, 
                exchanges, ein, description, website, investorWebsite, category, 
                fiscalYearEnd, stateOfIncorporation, stateOfIncorporationDescription, phone, 
                flags, mailing_street1, mailing_street2, mailing_city, mailing_stateOrCountry, 
                mailing_zipCode, mailing_stateOrCountryDescription, business_street1, 
                business_street2, business_city, business_stateOrCountry, business_zipCode, 
                business_stateOrCountryDescription

For get_information_table and download_information_table:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:param table_type: The table to query (default is "INFORMATION_TABLE")
:param columns: Specific columns to return. If None, all columns are returned.
:param name_of_issuer: Name of the issuing company (string, list, or None)
:param title_of_class: Class of securities (string, list, or None)
:param cusip: CUSIP identifier (string, list, or None)
:param value: Value of holdings in $ (numeric, tuple for range, or None)
:param ssh_prnamt: Number of shares held (numeric, tuple for range, or None)
:param ssh_prnamt_type: Type of shares (e.g., SH for shares) (string, list, or None)
:param investment_discretion: Level of investment discretion (string, list, or None)
:param voting_authority_sole: Shares with sole voting authority (numeric, tuple for range, or None)
:param voting_authority_shared: Shares with shared voting authority (numeric, tuple for range, or None)
:param voting_authority_none: Shares with no voting authority (numeric, tuple for range, or None)
:param reporting_owner_cik: CIK of the reporting owner (string, list, or None)
:param put_call: Put or call indicator (string, list, or None)
:param other_manager: Other managers reporting the security (string, list, or None)
:param figi: Financial Instrument Global Identifier (string, list, or None)
:param accession: SEC filing accession number (string, list, or None)
:param filing_date: Date of filing (string, list, or tuple for date range)
:param api_key: SEC BigQuery API key. If None, looks for DATAMULE_API_KEY env variable.
:param print_cost: Whether to print the query cost information
:param verbose: Whether to print additional information about the query

Additional parameters for download_information_table:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:param filepath: Path where to save the CSV file. If relative, it will be relative to the Sheet's path.

Free Datasets
-------------
* XBRL (via sec, free)
* Institutional Holdings (via datamule, paid), constructed from 13F-HR INFORMATION TABLE
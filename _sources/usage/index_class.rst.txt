Index
=====

Index is a class that allows you to search SEC submissions using simple or complex search terms. 

..
    Index will have records in the future

Methods
-------

``search_submissions(text_query=None, start_date=None, end_date=None, submission_type=None, cik=None, ticker=None, requests_per_second=5.0, quiet=False, **kwargs)``
    Retrieves SEC filing data matching the specified criteria and saves it to disk.

Parameters
~~~~~~~~~~
    :param text_query: Text to search for in SEC filings.
    :start_date: Start date for filing search. Format 'YYYY-MM-DD'.
    :end_date: End date for filing search. Format 'YYYY-MM-DD'.
    :submission_type: Type of SEC submission to search (e.g., '10-K', '10-Q', '8-K').
    :cik: CIK(s) to filter by. Company identifier(s).
    :ticker: Ticker(s) to filter by. Stock symbol(s).
    :requests_per_second: Rate limit for API requests. Default is 5. Will immediately break if set to > 10, will break for > 5 if used for extended periods.
    :quiet: Whether to suppress output. Default is True.

Text Query Syntax
~~~~~~~~~~~~~~~~~
The ``text_query`` parameter supports a modified Elasticsearch syntax with the following operators:

1. Boolean Operators
   - ``term1 AND term2`` - Both terms must appear
   - ``term1 OR term2`` - Either term can appear
   - ``term1 NOT term2`` or ``term1 -term2`` - Excludes documents containing the second term
   - Example: ``revenue AND growth NOT decline``

2. Exact Phrase Matching
   - Using double quotes for exact phrase matching
   - Example: ``"revenue growth"``

3. Wildcards
   - Single character (``?``) and multiple character (``*``) wildcards
   - Example: ``ris* factor?`` - Matches "risk factors", "rise factorx", etc.

4. Boosting
   - Using double asterisk (``**``) followed by a number to increase term importance
   - Example: ``revenue**2 growth`` - Makes "revenue" twice as important

Limitations to Note
^^^^^^^^^^^^^^^^^^^
- **Complex Nesting**: Avoid using parentheses for grouping as they may be interpreted as literal search terms
  - Instead of: ``(revenue OR sales) AND growth``
  - Use: ``revenue AND growth OR sales AND growth``

- **Proximity & Fuzzy Searches**: This implementation does not support proximity searches with the tilde operator (``~``) or fuzzy matching

    
Additional Search Criteria
~~~~~~~~~~~~~~~~~~~~~~~~~~
:param \**kwargs: Additional search criteria including:
    name (str): Company name
    entityType (str): Type of entity
    sic (str): Standard Industrial Classification code
    sicDescription (str): Description of SIC code
    ownerOrg (str): Owner organization
    insiderTransactionForOwnerExists (bool): Filter by insider transaction for owner
    insiderTransactionForIssuerExists (bool): Filter by insider transaction for issuer
    exchanges (str or list): Stock exchange(s)
    ein (str): Employer Identification Number
    description (str): Company description
    website (str): Company website URL
    investorWebsite (str): Investor relations website URL
    category (str): Company category
    fiscalYearEnd (str): Fiscal year end date
    stateOfIncorporation (str): State of incorporation
    stateOfIncorporationDescription (str): Description of state of incorporation
    phone (str): Company phone number
    flags (str or list): Special flags
    mailing_street1 (str): Mailing address street line 1
    mailing_street2 (str): Mailing address street line 2
    mailing_city (str): Mailing address city
    mailing_stateOrCountry (str): Mailing address state or country code
    mailing_zipCode (str): Mailing address ZIP code
    mailing_stateOrCountryDescription (str): Description of mailing state or country
    business_street1 (str): Business address street line 1
    business_street2 (str): Business address street line 2
    business_city (str): Business address city
    business_stateOrCountry (str): Business address state or country code
    business_zipCode (str): Business address ZIP code
    business_stateOrCountryDescription (str): Description of business state or country

Returns
~~~~~~~
    dict: A dictionary containing search results

Results Format
~~~~~~~~~~~~~~
The ``search_submissions`` method returns a dictionary containing search results. Each result entry includes:

.. code-block:: python

    {
        "_index": "edgar_file",
        "_id": "0001628280-24-002390:tsla-2023x12x31xex211.htm",
        "_score": 10.79173,
        "_source": {
            "ciks": ["0001318605"],
            "period_ending": "2023-12-31",
            "file_num": ["001-34756"],
            "display_names": ["Tesla, Inc.  (TSLA)  (CIK 0001318605)"],
            "xsl": null,
            "sequence": 2,
            "root_forms": ["10-K"],
            "file_date": "2024-01-29",
            "biz_states": ["CA"],
            "sics": ["3711"],
            "form": "10-K",
            "adsh": "0001628280-24-002390",
            "film_num": ["24569853"],
            "biz_locations": ["Palo Alto, CA"],
            "file_type": "EX-21.1",
            "file_description": "EX-21.1",
            "inc_states": ["DE"],
            "items": []
        }
    }

Key Components of Results
^^^^^^^^^^^^^^^^^^^^^^^^^
- ``_id``: Contains the document identifier in the format accession_number:matched document within a submission
- ``_score``: Elasticsearch relevance score indicating match quality
- ``_source``: Contains metadata about the filing, including:
  - ``ciks``: Company identifiers
  - ``period_ending``: End date of the reporting period
  - ``display_names``: Company name with ticker and CIK
  - ``root_forms``: Primary form type
  - ``file_date``: Date the document was filed
  - ``form``: Specific form type
  - ``adsh``: Accession number
  - ``file_type``: Document type within the filing

Examples
~~~~~~~~
.. code-block:: python

    # Search for "risk factors" in Apple's 10-K filings
    index = Index()
    results = index.search_submissions(
        text_query='"risk factors"',
        submission_type="10-K",
        ticker="AAPL",
        start_date="2020-01-01",
        end_date="2023-12-31"
    )

    # Search for "war" but exclude "peace" in 10-K filings from January 2023 using 3 requests per second
    results = index.search_submissions(
        text_query='war NOT peace',
        submission_type="10-K",
        start_date="2023-01-01",
        end_date="2023-01-31",
        quiet=False,
        requests_per_second=3
    )

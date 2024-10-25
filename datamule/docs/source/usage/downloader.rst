Downloader
=========

The Downloader module provides functionality for downloading SEC filings and related data.

Basic Usage
----------

.. code-block:: python

    downloader = dm.Downloader()

Downloading Filings
-----------------

The downloader uses the `EFTS API <https://efts.sec.gov/LATEST/search-index>`_ to retrieve filing locations, and the SEC API to download filings.

Important Note: form is root form type (e.g., '10-K' includes '10-K/A'). To filter use **file_types** set to e.g. '10-K'.

Parameters
~~~~~~~~~

The ``download()`` method accepts the following parameters:

- **output_dir** (str, optional): Directory where downloaded filings will be saved. Defaults to 'filings'.
- **return_urls** (bool, optional): If True, returns list of filing URLs instead of downloading them. Defaults to False.
- **cik** (str|list, optional): Central Index Key(s) of companies. Can be single CIK or list of CIKs. Will be zero-padded to 10 digits.
- **ticker** (str|list, optional): Stock ticker symbol(s). Will be converted to CIK. Mutually exclusive with cik parameter.
- **form** (str|list, optional): SEC form type(s) to download. Forms include all variations (e.g., '10-K' includes '10-K/A'). Examples:
    - Single form: "10-K", "10-Q", "8-K"
    - Multiple forms: ["10-K", "10-Q"]
    - Defaults to "-0" (all forms)
- **date** (str|tuple|list, optional): Filing date criteria. Can be:
    - Single date: "2023-01-01"
    - Date range tuple: ("2023-01-01", "2023-12-31")
    - List of dates: ["2023-01-01", "2023-02-01"]
    - Defaults to all dates from 2001-01-01 to present
- **sics** (list, optional): Standard Industrial Classification codes to filter by. Example: [1311, 2834]
- **items** (list, optional): Form-specific item numbers to filter by. Example: ["1.01", "2.01"] for 8-K items
- **file_types** (str|list, optional): Types of files to download, such as exhibits. Examples: "EX-10", ["EX-10", "EX-21"]

Examples
~~~~~~~~

.. code-block:: python

    # Download all 10-K filings (including 10-K/A) for Tesla using CIK
    downloader.download(form='10-K', cik='1318605', output_dir='filings')

    # Download 10-K filings for multiple companies using tickers
    downloader.download(form='10-K', ticker=['TSLA', 'META'], output_dir='filings')

    # Download every form 3 for a specific date
    downloader.download(form='3', date='2024-05-21', output_dir='filings')

    # Download filings with specific exhibit types
    downloader.download(form='10-K', ticker='AAPL', file_types=['EX-10', 'EX-21'])

    # Download 8-K filings with specific items
    downloader.download(form='8-K', ticker='TSLA', items=['1.01', '2.01'])

Rate Limits
----------

The default rate limit is set to 10 requests/second. You can modify this:

.. code-block:: python

    downloader.set_limiter('www.sec.gov', 5)

Monitoring New Filings
--------------------

You can watch for new filings:

.. code-block:: python

    downloader.watch(interval=1, form='8-K', ticker='AAPL')
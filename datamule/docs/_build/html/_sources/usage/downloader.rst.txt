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

.. code-block:: python

    # Download all 10-K filings for Tesla using CIK
    downloader.download(form='10-K', cik='1318605', output_dir='filings')

    # Download 10-K filings for multiple companies using tickers
    downloader.download(form='10-K', ticker=['TSLA', 'META'], output_dir='filings')

    # Download every form 3 for a specific date
    downloader.download(form='3', date='2024-05-21', output_dir='filings')

Rate Limits
----------

The default rate limit is set to 7 requests/second. You can modify this:

.. code-block:: python

    downloader.set_limiter('www.sec.gov', 10)

Monitoring New Filings
--------------------

You can watch for new filings:

.. code-block:: python

    downloader.watch(interval=1, form='8-K', ticker='AAPL')
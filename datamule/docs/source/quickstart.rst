Quick Start
==========

Basic Usage
----------

Here's a simple example to get you started:

.. code-block:: python

    import datamule as dm

    downloader = dm.Downloader()
    downloader.download(form='10-K', ticker='AAPL')

Package Data
-----------

The package includes several useful CSV datasets:

- ``company_former_names.csv``: Former names of companies
- ``company_metadata.csv``: Metadata including SIC classification
- ``company_tickers.csv``: CIK, ticker, name mappings
- ``sec-glossary.csv``: Form types and descriptions
- ``xbrl_descriptions.csv``: Category fact descriptions

Updating Package Data
-------------------

You can update the package data using:

.. code-block:: python

    downloader.update_company_tickers()
    downloader.update_metadata()

API Key
-------

Some datasets and features require an API key. [WIP]
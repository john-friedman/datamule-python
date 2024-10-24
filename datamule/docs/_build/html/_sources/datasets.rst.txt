Datasets
========

Available Datasets
----------------

datamule provides access to several SEC datasets:

- **FTD Data** (1.3GB, ~60s to download)
    * Every FTD since 2004
    * ``dataset='ftd'``

- **10-Q Filings**
    * Every 10-Q since 2001
    * 500MB-3GB per year, ~5 minutes to download
    * ``dataset='10q_2023'`` (replace year as needed)

- **10-K Filings**
    * Every 10-K from 2001 to September 2024
    * ``dataset='10k_2002'`` (replace year as needed)

- **13F-HR Information Tables**
    * Every 13F-HR Information Table since 2013
    * Updated to current date
    * ``dataset='13f_information_table'``

- **MD&A Collection**
    * 100,000 MD&As since 2001
    * Requires free API key (beta)

Usage Example
-----------

.. code-block:: python

    downloader.download_dataset(dataset='ftd')
    downloader.download_dataset(dataset='10q_2023')
    downloader.download_dataset(dataset='13f_information_table')

Notes
-----

* Bulk datasets may become out of date. Use ``download_dataset()`` + ``download()`` to fill gaps
* The 13f_information_table dataset automatically implements gap-filling

Package Data
-----------

The package includes several useful CSV datasets:

- ``company_former_names.csv``: Former names of companies
- ``company_metadata.csv``: Metadata including SIC classification
- ``company_tickers.csv``: CIK, ticker, name mappings
- ``sec-glossary.csv``: Form types and descriptions
- ``xbrl_descriptions.csv``: Category fact descriptions

Usage Example

.. code-block:: python
    
    from datamule import load_package_dataset
    company_tickers = pd.DataFrame(load_package_dataset('company_tickers'))

Updating Package Data
-------------------

You can update the package data using:

.. code-block:: python

    downloader.update_company_tickers()
    downloader.update_metadata()
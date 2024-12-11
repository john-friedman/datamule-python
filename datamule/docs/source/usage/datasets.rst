Datasets
========

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

    from datamule import PackageUpdater

    package_updater = PackageUpdater()
    package_updater.update_company_tickers()
    package_updater.update_metadata()
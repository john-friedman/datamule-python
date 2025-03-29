Sheet
=====

Sheet is a class that allows you to download tabular datasets.

..
    Sheet will have leaves in the future

Functions
---------

``download_xbrl(cik, **kwargs)``
    Retrieves the data and saves it to disk. if cik is not provided, all data will be downloaded.

Shared Parameters
~~~~~~~~~~~~~~~~~
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
    

Free Datasets
-------------
* XBRL (via sec, free)

Premium Datasets (Forthcoming)
------------------------------
* XBRL
* 345
* 13F-HR
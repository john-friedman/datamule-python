Examples
========

Basic Downloads
-------------

Download 10-K filings for specific companies:

.. code-block:: python

    import datamule as dm
    
    downloader = dm.Downloader()
    
    # Download by CIK
    downloader.download(form='10-K', cik='1318605')
    
    # Download by ticker
    downloader.download(form='10-K', ticker=['TSLA', 'META'])

Working with XBRL Data
--------------------

Parse and analyze XBRL data:

.. code-block:: python

    from datamule import parse_company_concepts
    
    # Download company concepts
    downloader.download_company_concepts(ticker='AAPL')
    
    # Parse the data
    tables = parse_company_concepts(company_concepts)

Using MuleBot
-----------

Set up a MuleBot instance:

.. code-block:: python

    from datamule.mulebot import MuleBot
    
    mulebot = MuleBot(openai_api_key="your-api-key")
    mulebot.run()

For more examples, check out our `GitHub repository <https://github.com/john-friedman/datamule-python/tree/main/examples>`_.
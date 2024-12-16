Quickstart
==========

Downloading submissions (Free)
------------------------------

.. code-block:: python

    from datamule import Downloader
    downloader = Downloader()
    downloader.download_filings(
        output_dir='ford8k',
        ticker='F',
        form=['8-K']
    )


Downloading submissions (Premium)
---------------------------------

.. code-block:: python

    from datamule import PremiumDownloader
    downloader = PremiumDownloader(api_key="dm....")
    downloader.download_filings(
        output_dir='ford_4',
        ticker='F',
        form=['4']
    )

Parsing submissions
-------------------
.. code-block:: python
    
    from datamule import Portfolio
    import pandas as pd

    portfolio = Portfolio('ford_4')
    for submission in portfolio:
        for form_4 in submission.document_type('4'):
            print(pd.DataFrame(form_4))
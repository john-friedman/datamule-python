Downloader & Premium Downloader
===============================

Downloader is free, but constrained by SEC rate limits. Premium Downloader uses the `datamule api <https://datamule.xyz/products>`_ which is constrained by your internet speed and hardware.

Downloader
----------
.. code-block:: python
    
    from datamule import Downloader
    downloader = Downloader()

    # Download SEC filings
    download_submissions(
        self,
        output_dir='filings',  # Where to save files
        cik=None,             # CIK number, list of CIKs, or None for all
        ticker=None,          # Stock symbol, list of symbols, or None
        submission_type=None,            # Submission types: '10-K', ['10-K', '10-Q', '8-K']
        filing_date=None            # Filing dates:
                            # * Single date: "2023-01-01"
                            # * Date range tuple: ("2023-01-01", "2023-12-31")
                            # * List of dates: ["2023-01-01", "2023-02-01"]
                            # * Defaults to all dates from 2001-01-01 to present
    )

    # Download XBRL company concepts (financial data)
    download_company_concepts(
        self,
        output_dir='company_concepts',  # Where to save XBRL JSON files
        cik=None,                      # CIK number, list of CIKs, or None for all
        ticker=None                    # Stock symbol, list of symbols, or None
    )

Premium Downloader
----------------
.. code-block:: python

    from datamuler import PremiumDownloader as Downloader
    downloader = Downloader(api_key='your-api-key') # will automatically use the environment variable DATAMULE_API_KEY

    # Download SEC filings
    download_submissions(
        self,
        output_dir='filings',  # Where to save files
        cik=None,             # CIK number, list of CIKs, or None for all
        ticker=None,          # Stock symbol, list of symbols, or None
        submission_type=None,            # Submission types: '10-K', ['10-K', '10-Q', '8-K']
        filing_date=None            # Filing dates:
                            # * Single date: "2023-01-01"
                            # * Date range tuple: ("2023-01-01", "2023-12-31")
                            # * List of dates: ["2023-01-01", "2023-02-01"]
                            # * Defaults to all dates from 2001-01-01 to present
    )

Pricing
=======

* **Free**: Basic Downloader
* **Premium Tier**: $1/100,000 filings + $1/billion rows read (the database is 16 million rows total, so max read cost is about 1.6 cents).

Query Optimization
==================
The database uses a composite index (submission_type, filing_date, cik). For optimal performance and lower costs:

* Use columns in left-to-right order:
  * ``submission_type``
  * ``submission_type + filing_date``
  * ``submission_type + filing_date + cik``

.. note::
   Queries using only ``filing_date`` or ``cik`` will not leverage the index efficiently.

.. note:: 
   In the future, I'll add more indexes that will remove the need for this optimization. I would do it now, but it would cost me $50. Waiting for next month, when my write quota resets.

.. note::
    API returns up to 25,000 results per page.

Performance Tuning for Premium Downloader
----------------
You can adjust these parameters to optimize for your hardware:

.. code-block:: python

    # Defaults
    downloader.CHUNK_SIZE = 2 * 1024 * 1024              # 2MB chunks
    downloader.MAX_CONCURRENT_DOWNLOADS = 100            # Parallel downloads
    downloader.MAX_DECOMPRESSION_WORKERS = 16           # Decompression threads
    downloader.MAX_PROCESSING_WORKERS = 16              # Processing threads
    downloader.QUEUE_SIZE = 10                          # Internal queue size

API key
^^^^^^^

PowerShell
~~~~~~~~~~
.. code-block:: powershell

    [System.Environment]::SetEnvironmentVariable('DATAMULE_API_KEY', 'your-api-key', 'User')

Bash
~~~~
.. code-block:: bash

    echo 'export DATAMULE_API_KEY="your-api-key"' >> ~/.bashrc
    source ~/.bashrc

Zsh (macOS default)
~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    echo 'export DATAMULE_API_KEY="your-api-key"' >> ~/.zshrc
    source ~/.zshrc

Note: after setting the environment variable, you may need to restart your terminal/shell for the changes to take effect.

Benchmarks
----------

+---------------+--------------------+--------------------+--------------------+
| File Size     | Examples          | Downloader         | Premium Downloader |
+===============+====================+====================+====================+
| Small Files   | 3, 4, 5           | 5/s                | 300/s             |
+---------------+--------------------+--------------------+--------------------+
| Medium Files  | 8-K               | 5/s                | 60/s              |
+---------------+--------------------+--------------------+--------------------+
| Large Files   | 10-K              | 3/s                | 5/s               |
+---------------+--------------------+--------------------+--------------------+

Note 1: Premium Downloader may be much faster depending on your laptop's specs and internet connection.

Note 2: Premium Downloader will be updated soon to be 10-100x faster.
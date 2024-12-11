Welcome to datamule's documentation!  
====================================  

A Python package to work with SEC submissions at scale. Integrated with `datamule <https://datamule.xyz/>`_'s APIs and datasets.  

Features  
--------  
- Download SEC submissions quickly and easily using the `Downloader <usage/downloader>`_ or `Premium Downloader <usage/premium_downloader>`_.  
- Monitor EDGAR for new submissions using `Monitor <usage/monitor>`_. 
- Parse 13F-HR-INFORMATIONTABLE, 8-K, 10-K, 10-Q, 3, 4, 5, D, NPORT-P, SC 13D, and SC 13G. Will be updated soon to include almost all SEC form types and attachments `Parser <usage/parser>`_.
- Create alternate datasets directly from SEC submissions' unstructured text using `DatasetBuilder <usage/dataset_builder>`_. 
- Access datasets such as:  
  - **Company Metadata (includes SIC Codes)**: `https://raw.githubusercontent.com/john-friedman/datamule-python/refs/heads/main/datamule/datamule/data/company_metadata.csv`_.  
  - **Company Former Names**: `https://raw.githubusercontent.com/john-friedman/datamule-python/refs/heads/main/datamule/datamule/data/company_former_names.csv`_.  
  - **Company Tickers**: `https://raw.githubusercontent.com/john-friedman/datamule-python/refs/heads/main/datamule/datamule/data/company_tickers.csv`_.  
  - **Glossary of SEC Submission Types**: `https://raw.githubusercontent.com/john-friedman/datamule-python/refs/heads/main/datamule/datamule/data/sec-glossary.csv`_.  
  - **XBRL Descriptions**: `https://raw.githubusercontent.com/john-friedman/datamule-python/refs/heads/main/datamule/datamule/data/xbrl_descriptions.csv`_.  
- Interact with SEC data using MuleBot.  `MuleBot <usage/mulebot>`_.

.. note::  
   I built MuleBot in a day to learn how tool-calling chatbots with artifacts work. I'm planning to make it useful in the future. Still fun to play with!


Benchmarks
----------

+---------------+--------------------+--------------------+--------------------+
| File Size     | Examples          | Downloader         | Premium Downloader |
+===============+====================+====================+====================+
| Small Files   | 3, 4, 5           | 5/s                | 300/s              |
+---------------+--------------------+--------------------+--------------------+
| Medium Files  | 8-K               | 5/s                | 60/s               |
+---------------+--------------------+--------------------+--------------------+
| Large Files   | 10-K              | 3/s                | 5/s                |
+---------------+--------------------+--------------------+--------------------+

Note 1: Premium Downloader may be much faster depending on your laptop's specs and internet connection.
Note 2: Premium Downloader will be updated soon to be 10-100x faster.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   usage/index
   known_issues
   changelog

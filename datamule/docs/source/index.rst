====================================
Welcome to datamule's documentation!
====================================

A Python package to work with SEC submissions at scale. Integrated with `datamule's <https://datamule.xyz/>`_ APIs and datasets.

Features
========

Core Functionality
----------------

* **Fast SEC Downloads**: Utilize the `Downloader <usage/downloader/downloader>`_ or `Premium Downloader <usage/downloader/premium_downloader>`_ to download SEC filings.

* **Real-time Monitoring**: Keep track of new EDGAR submissions using `Monitor <usage/monitor>`_.

* **Interact with SEC Submissions**: Access, parse, and interact with SEC submissions using `Portfolio <usage/core_classes#portfolio>`_, `Submission <usage/core_classes#submission>`_, and `Document <usage/core_classes#document>`_.


Available Datasets
------------------

Access SEC-related datasets:

* `Company Metadata`_ (including SIC Codes)
* `Company Former Names`_
* `Company Tickers`_
* `SEC Submission Types Glossary`_
* `XBRL Descriptions`_

.. _Company Metadata: https://raw.githubusercontent.com/john-friedman/datamule-python/refs/heads/main/datamule/datamule/data/company_metadata.csv
.. _Company Former Names: https://raw.githubusercontent.com/john-friedman/datamule-python/refs/heads/main/datamule/datamule/data/company_former_names.csv
.. _Company Tickers: https://raw.githubusercontent.com/john-friedman/datamule-python/refs/heads/main/datamule/datamule/data/company_tickers.csv
.. _SEC Submission Types Glossary: https://raw.githubusercontent.com/john-friedman/datamule-python/refs/heads/main/datamule/datamule/data/sec-glossary.csv
.. _XBRL Descriptions: https://raw.githubusercontent.com/john-friedman/datamule-python/refs/heads/main/datamule/datamule/data/xbrl_descriptions.csv

MuleBot Integration
-------------------

.. note::
   I built MuleBot in a day to learn how tool-calling chatbots with artifacts work. I'm planning to make it useful in the future. Still fun to play with!

Navigation
==========

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   usage/index
   examples
   changelog
   api_key
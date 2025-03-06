========
datamule
========

A Python package to work with SEC submissions at scale. Integrated with `datamule's <https://datamule.xyz/>`_ APIs and datasets.

Features
========

* Download SEC submissions using the SEC (free, 5/s) or datamule ($1/100,000 but no rate limits)
* Monitor the SEC for new submissions
* Parse SEC submissions

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


.. note::
   Feel free to contact me for free credits.

Navigation
==========

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   api_key
   quickstart
   usage/index
   examples
   changelog

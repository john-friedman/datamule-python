========
datamule
========

A Python package to work with SEC submissions at scale. Integrated with `datamule's <https://datamule.xyz/>`_ APIs and datasets.

Features
========

* Download SEC submissions using the SEC (free, 5/s) or datamule ($1/100,000 but no rate limits)
* Monitor the SEC for new submissions
* Parse SEC submissions

Core Classes
============

* **Portfolio**: Download & manipulate SEC submissions.
* **Sheet**: Download tabular datasets such as XBRL.
* **Index**: Search SEC Submissions using simple or complex search terms, just like using a search engine.

Available Datasets
------------------

Checkout: `datamule-data <https://github.com/john-friedman/datamule-data>`_.

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
   utils/index
   changelog

Datamule
========

.. image:: https://static.pepy.tech/badge/datamule
   :target: https://pepy.tech/project/datamule
   :alt: Downloads

.. image:: https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fjohn-friedman%2Fdatamule-python&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false
   :target: https://hits.seeyoufarm.com
   :alt: Hits

.. image:: https://img.shields.io/github/stars/john-friedman/datamule-python
   :alt: GitHub Stars

A Python package for working with SEC filings at scale. 
`Full Documentation <https://john-friedman.github.io/datamule-python/>`_ | 
`Website <https://datamule.xyz/>`_

Related packages:
-----------------

* `datamule-data <https://github.com/john-friedman/datamule-data/>`_ Contains datasets for use with datamule-python
* `datamule-indicators <https://github.com/john-friedman/datamule-indicators/>`_  Create economic indicators from SEC filings
* `txt2dataset <https://github.com/john-friedman/txt2dataset/>`_  Create datasets from unstructured text
* `secsgml <https://github.com/john-friedman/secsgml/>`_ Parse SEC filings in SGML format
* `doc2dict <https://github.com/john-friedman/doc2dict>`_ Convert documents to dictionaries. Not ready for public use.


Features
--------

* Download SEC filings quickly and efficiently
* Monitor EDGAR for new filings in real-time
* Parse filings at scale
* Access comprehensive datasets (10-Ks, SIC codes, etc.)

Quick Start
-----------

Basic Installation
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install datamule

Basic Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datamule import Portfolio

   # Create a Portfolio object
   portfolio = Portfolio('output_dir') # can be an existing directory or a new one

   # Download submissions
   portfolio.download_submissions(
      filing_date=('2023-01-01','2023-01-03'),
      submission_type=['10-K']
   )

   # Iterate through documents by document type
   for ten_k in portfolio.document_type('10-K'):
      ten_k.parse()
      print(ten_k.data['document']['part2']['item7'])

   # Iterate through documents by what strings they contain
   for document in portfolio.contains_string('United States'):
      print(document.path)

   # You can also use regex patterns
   for document in portfolio.contains_string(r'(?i)covid-19'):
      print(document.type)

   # For faster operations, you can take advantage of built in threading with callback function
   def callback(submission):
      print(submission.path)

   submission_results = portfolio.process_submissions(callback) 


Examples (Out of Date - Will be updated soon)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a discord bot, use insider trading disclosures to map relationships in Silicon Valley, and more in `examples <https://github.com/john-friedman/datamule-python/tree/main/examples>`_.

Data Provider
~~~~~~~~~~~~~

Default is the SEC, but for faster downloads you can use datamule.

.. code-block:: python

   from datamule import Config

   config = Config()
   config.set_default_source("datamule") # set default source to datamule, can also be "sec"
   print(f"Default source: {config.get_default_source()}")

To use datamule as a provider, you need an `API key <https://datamule.xyz/dashboard>`_.


Articles
--------
* `How to host the SEC Archive for $20/month <https://medium.com/@jgfriedman99/how-to-host-the-sec-archive-for-20-month-da374cc3c3fb>`_
* `Creating Structured Datasets from SEC filings <https://medium.com/@jgfriedman99/how-to-create-alternative-datasets-using-datamule-d3a0192da8f6>`_
* `Deploy a Financial Chatbot in 5 Minutes <https://medium.com/@jgfriedman99/how-to-deploy-a-financial-chatbot-in-5-minutes-ef5eec973d4c>`_

.. image:: https://api.star-history.com/svg?repos=john-friedman/datamule-python&type=Date
   :target: https://star-history.com/#john-friedman/datamule-python
   :alt: Star History Chart


License
-------

`MIT License <LICENSE>`_
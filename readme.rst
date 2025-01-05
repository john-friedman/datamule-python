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

Features
--------

* `Download SEC filings quickly and efficiently <https://john-friedman.github.io/datamule-python/usage/downloader.html>`_
* `Monitor EDGAR for new filings in real-time <https://john-friedman.github.io/datamule-python/usage/monitor.html>`_
* `Parse filings at scale <https://john-friedman.github.io/datamule-python/usage/parsing.html>`_
* `Access comprehensive datasets (10-Ks, SIC codes, etc.) <https://john-friedman.github.io/datamule-python/usage/datasets.html>`_
* `Build datasets directly from unstructured text <https://john-friedman.github.io/datamule-python/usage/dataset_builder.html>`_
* `Interact with SEC data using MuleBot <https://john-friedman.github.io/datamule-python/usage/mulebot.html>`_

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


Examples
~~~~~~~~

Create a discord bot, use insider trading disclosures to map relationships in Silicon Valley, and more in `examples <https://github.com/john-friedman/datamule-python/tree/main/examples>`_.

Data Provider
~~~~~~~~~~~~~

Default is the SEC, but for faster downloads you can use datamule.

.. code-block:: python

   from datamule import Config

   config = Config()
   config.set_default_source("datamule") # set default source to datamule, can also be "sec"
   print(f"Default source: {config.get_default_source()}")

To use datamule as a provider, you need an `API key <https://datamule.xyz/dashboard>`_. It costs $1/100,000 downloads.

.. list-table:: Benchmarks
   :widths: 20 20 20 40
   :header-rows: 1

   * - File Size
     - Examples
     - Downloader
     - Premium Downloader
   * - Small Files
     - 3, 4, 5
     - 5/s
     - 300/s
   * - Medium Files
     - 8-K
     - 5/s
     - 60/s
   * - Large Files
     - 10-K
     - 3/s
     - 5/s


Articles
--------
* `How to download SEC filings in 2025 <https://medium.com/@jgfriedman99/how-to-download-sec-filings-in-2025-ecaa023a81ac>`_
* `How to host the SEC Archive for $20/month <https://medium.com/@jgfriedman99/how-to-host-the-sec-archive-for-20-month-da374cc3c3fb>`_
* `Creating Structured Datasets from SEC filings <https://medium.com/@jgfriedman99/how-to-create-alternative-datasets-using-datamule-d3a0192da8f6>`_
* `Deploy a Financial Chatbot in 5 Minutes <https://medium.com/@jgfriedman99/how-to-deploy-a-financial-chatbot-in-5-minutes-ef5eec973d4c>`_

License
-------

`MIT License <LICENSE>`_
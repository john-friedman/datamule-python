Portfolio
=========

Portfolio is used to interact with SEC submissions.

Quickstart
----------

Initialization
~~~~~~~~~~~~~~
.. code-block:: python

   from datamule import Portfolio

   # Create a Portfolio object
   portfolio = Portfolio('climate') # need to modify this docs

   # Filter submissions
   portfolio.filter_text('"climate change" risks', filing_date=('2019-01-01', '2019-01-31'), submission_type='10-K')

Downloading Submissions
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Download submissions - note that filters are applied here
   portfolio.download_submissions(submission_type='10-K', filing_date=('2019-01-01', '2019-01-31'), provider='sec')

Processing Submissions
~~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: python

   def callback_function(submission):
      try:
         print(submission.metadata['cik'])
      except:
         print(submission.metadata['central index key'])

   # Process submissions - note that filters are applied here
   portfolio.process_submissions(submission_type='10-K', filing_date=('2019-01-01', '2019-01-31'), provider='sec', submission_callback=callback_function)


Functions
---------

Submissions
~~~~~~~~~~~

``process_submissions(submission_callback, cik=None, ticker=None, submission_type=None, filing_date=None, provider=None, **kwargs)``
   Processes submissions.

   :param submission_callback: Function to call for each submission
   :param provider: Data provider to use for retrieval

``download_submissions(output_dir='submissions', cik=None, ticker=None, submission_type=None, filing_date=None, provider=None, **kwargs)``
   Retrieves the submissions and saves them to disk.

   :param output_dir: Directory to save the submissions
   :param provider: Data provider to use for retrieval


Filters
~~~~~~~

Run this before Submissions.

``filter_text(text_query, cik=None, submission_type=None, filing_date=None, requests_per_second=5.0, **kwargs)``
   filters submissions by text.

   :param text_query: Text to search for in the submission. Use double quotes for exact matches. E.g. '"Climate Change"' or '"Climate Change" risks'

``filter_xbrl(taxonomy, concept, unit, period, logic, value)``
   :param taxonomy: XBRL taxonomy e.g. 'dei'
   :param concept: XBRL concept e.g. 'EntityCommonStockSharesOutstanding'
   :param unit: XBRL unit e.g. 'shares'
   :param period: XBRL period e.g. 'CY2019Q4I'
   :param logic: Logic operator to use for filtering, e.g. '>', '<', '>=', '<=', '==', '!='
   :param value: Value to compare against


.. note::
   parameters for a company can be found `here <https://data.sec.gov/api/xbrl/companyfacts/CIK0001318605.json>`_


Shared Parameters for download_submissions, process_submissions, and filter_text
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:param cik: Central Index Key identifier for the company
:param ticker: Stock ticker symbol
:param submission_type: Type of filing (e.g. "10-K", "10-Q", "8-K")
:param filing_date: Date of the filing
:param \**kwargs: Additional search criteria including name, entityType, sic, sicDescription, 
                ownerOrg, insiderTransactionForOwnerExists, insiderTransactionForIssuerExists, 
                exchanges, ein, description, website, investorWebsite, category, 
                fiscalYearEnd, stateOfIncorporation, stateOfIncorporationDescription, phone, 
                flags, mailing_street1, mailing_street2, mailing_city, mailing_stateOrCountry, 
                mailing_zipCode, mailing_stateOrCountryDescription, business_street1, 
                business_street2, business_city, business_stateOrCountry, business_zipCode, 
                business_stateOrCountryDescription




Monitoring
~~~~~~~~~~

monitor_submissions(self,data_callback=None, poll_callback=None, submission_type=None, cik=None, 
           polling_interval=200, requests_per_second=5, quiet=False, start_date=None, ticker=None, **kwargs)

``monitor_submissions(data_callback,poll_callback, submission_type, cik, polling_interval, requests_per_second, quiet, start_date, ticker, **kwargs)``
   Monitors for new submissions.

   :param data_callback: Function to call for each submission
   :param poll_callback: Function to call after each poll
   :param requests_per_second: Number of requests per second to make. Default is 5. You will be rate limited if you exceed this.
   :param polling_interval: Time in seconds to wait between polls. Default is 200.
   :param quiet: If True, suppresses output. Default is False.
   :param start_date: Date to start monitoring from. Default is today.

Submission Class
----------------

Submissions are the core of the Portfolio class.

.. note:: submission.metadata is useful

Document Class
--------------

Documents are the core of the Submission class.

.. note:: document.parse() is useful

.. note:: I will make the documentation better soon.
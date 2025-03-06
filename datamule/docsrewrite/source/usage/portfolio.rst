Portfolio
=========

Portfolio is used to interact with SEC submissions. If called from ``__main__`` it will utilize parallel processing for faster performance.

Functions
---------

Submissions
~~~~~~~~~~~

``process_submissions(submission_callback, cik=None, ticker=None, submission_type=None, filing_date=None, provider=None, **kwargs)``
   Retrieves the submissions and processes them. Does not save the data to disk, but will use saved submissions if available.

   :param submission_callback: Function to call for each submission

``download_submissions(output_dir='submissions', cik=None, ticker=None, submission_type=None, filing_date=None, provider=None, **kwargs)``
   Retrieves the submissions and saves them to disk.

   :param output_dir: Directory to save the submissions

Parameters for submission functions
```````````````````````````````````
:param cik: Central Index Key identifier for the company
:param ticker: Stock ticker symbol
:param submission_type: Type of filing (e.g. "10-K", "10-Q", "8-K")
:param filing_date: Date of the filing
:param provider: Data provider to use for retrieval
:param \**kwargs: Additional search criteria including name, entityType, sic, sicDescription, 
                ownerOrg, insiderTransactionForOwnerExists, insiderTransactionForIssuerExists, 
                exchanges, ein, description, website, investorWebsite, category, 
                fiscalYearEnd, stateOfIncorporation, stateOfIncorporationDescription, phone, 
                flags, mailing_street1, mailing_street2, mailing_city, mailing_stateOrCountry, 
                mailing_zipCode, mailing_stateOrCountryDescription, business_street1, 
                business_street2, business_city, business_stateOrCountry, business_zipCode, 
                business_stateOrCountryDescription

.. note::
   \**kwargs will get some love in the future. Handling for ciks having multiple values will be added. View the dataset here: `Company Metadata <https://raw.githubusercontent.com/john-friedman/datamule-python/refs/heads/main/datamule/datamule/data/company_metadata.csv>`_.


Filters
~~~~~~~

Runs before process_submissions.


``filter_text(text_query, cik=None, submission_type=None, filing_date=None, requests_per_second=5.0)``
   filters submissions by text.

``filter_xbrl(logic)``
   filters submissions by xbrl logic.

Parameters for filter functions
```````````````````````````````````
:param text_query: Text to search for in the submission. Use double quotes for exact matches. E.g. '"Climate Change"' or '"Climate Change" risks'

Monitoring
~~~~~~~~~~

``monitor_submissions(typical args)``
   Monitors for new submissions.

Submission Class
----------------

Submissions are the core of the Portfolio class.

submission.metadata

Document Class
--------------

Documents are the core of the Submission class.

document.parse()
document.load()

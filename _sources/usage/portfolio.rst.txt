Portfolio
=========

Portfolio is the easiest way to interact with SEC data.


.. code-block:: python

    from datamule import Portfolio

    # Create a Portfolio object
    portfolio = Portfolio('output_dir') # can be an existing directory or a new one

    # Download submissions
    portfolio.download_submissions(
        filing_date=('2023-01-01','2023-01-31'),
        submission_type=['4']
    )

    # Iterate through documents by document type
    for ten_k in portfolio.document_type('10-K'):
        print(ten_k.parse())

    # Iterate through documents by what strings they contain
    for document in portfolio.contains_string('Trade War'):
        print(document.path)

    # You can also use regex patterns
    for document in portfolio.contains_string(r'(?i)covid-19'):
        print(document.type)
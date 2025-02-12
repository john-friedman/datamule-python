Core Classes 
============

Portfolio
---------
Container for managing SEC submissions. Takes the ``output_dir`` from the Downloader or PremiumDownloader as input.

Methods::

    portfolio = Portfolio('output_dir')
    
    # Iterate through submissions
    for submission in portfolio:
        print(submission.metadata)

Submission
----------
A SEC submission containing documents and metadata.

Methods::

    # Keep only specific document types, delete others
    submission.keep(['4', 'GRAPHIC'])
    
    # Delete specific document types, keep others
    submission.drop(['GRAPHIC'])
    
    # Iterate through documents of specific type
    for doc in submission.document_type('4'):
        data = doc.parse()

Document
--------
A document within a submission. For example, an INFORMATION TABLE inside a 13F-HR, or a GRAPHIC inside a 10-K. You can access it as an iterable, if it is supported by the parser.

Methods::

    # Parse document content
    data = document.parse()
    
    # Write to JSON
    document.write_json('output.json')
    
    # Write to CSV
    document.write_csv('output.csv')

Usage Example
-------------
Example converting Form 4 filings to CSV::

    from datamule import Submission, Portfolio, PremiumDownloader
    import pandas as pd

    # I set my api_key using the environment variable 'DATAMULE_API_KEY'
    downloader = PremiumDownloader()

    # Downloads for me in about 1 minute (300/sec)
    downloader.download_submissions(
        filing_date=('2023-01-01','2023-01-31'),
        submission_type='4',
        output_dir='jan_23'
    )
    portfolio = Portfolio('jan_23')

    # This is not optimized for speed, but it's a good example of how to iterate over the portfolio
    # Takes about 1 minute to run
    df_list = []
    for submission in portfolio:
        for form_4 in submission.document_type('4'):
            df_list.append(pd.DataFrame(form_4))

    df = pd.concat(df_list)
    df.to_csv('jan_23.csv',index=False)
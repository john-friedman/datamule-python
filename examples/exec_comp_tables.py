from datamule import Portfolio

portfolio = Portfolio('exec_comp_apple')

portfolio.download_submissions(ticker='AAPL',submission_type='DEF 14A',filing_date='2023-01-12')
# this url  https://www.sec.gov/Archives/edgar/data/320193/000130817923000019/laap2023_def14a.htm

for sub in portfolio:
    for doc in sub:
        # DEF 14A are often filed in both html and pdf. I think html is required.
        if doc.extension in ['.htm','.html']:
            # match based on pattern
            # may need to tweak this for your use case
            exec_comp_tables = doc.get_tables(description_regex = r"compensation")
            for table in exec_comp_tables:
                print(table.description)
                print('\n')
                # Parsed from html, in [[],[],..] format
                print(table.data)
                print('-----')
                input('press any key to go to next table')


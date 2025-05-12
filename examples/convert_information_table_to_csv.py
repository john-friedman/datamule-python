from datamule import Portfolio

portfolio = Portfolio('informationtable')
portfolio.download_submissions(submission_type='13F-HR',document_type='INFORMATION TABLE',filing_date=('2023-01-01', '2023-01-11'))

for information_table in portfolio.document_type('INFORMATION TABLE'):
    information_table.write_csv('information_table')
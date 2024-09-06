from sec_downloader import Downloader
import sec_indexer

# Initialize the Downloader
downloader = Downloader()

# Example 1: Download all 10-K filings for Tesla using CIK
downloader.download(form='10-K', cik='1318605', output_dir='filings')

# Example 2: Download 10-K filings for Tesla and META using CIK
downloader.download(form='10-K', cik=['1318605','1326801'], output_dir='filings')

# Example 3: Download 10-K filings for Tesla using ticker
downloader.download(form='10-K', ticker='TSLA', output_dir='filings')

# Example 4: Download 10-K filings for Tesla and META using ticker
downloader.download(form='10-K', ticker=['TSLA','META'], output_dir='filings')

# Example 5: Download every form 3 for a specific date
downloader.download(form ='3', date='2024-05-21', output_dir='filings')

# Example 6: Download every 10K for a year
downloader.download(form='10-K', date=('2024-01-01', '2024-12-31'), output_dir='filings')

# Example 7: Download every form 4 for a list of dates
downloader.download(form = '4',date=['2024-01-01', '2024-12-31'], output_dir='filings')


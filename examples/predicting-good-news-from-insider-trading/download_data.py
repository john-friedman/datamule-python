from datetime import datetime, timedelta
from datamule import PremiumDownloader

print("Downloading Form 8-K filings day by day")

def get_last_day_of_month(year, month):
    # Get the first day of the next month
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    
    # Subtract one day to get the last day of the current month
    return (next_month - timedelta(days=1)).day

for month in range(1, 13):
    last_day = get_last_day_of_month(2024, month)
    
    # Iterate through each day of the month
    for day in range(1, last_day + 1):
        date_str = f'2024-{month:02d}-{day:02d}'
        
        print(f"Downloading 8-Ks for {date_str}")
        
        downloader = PremiumDownloader()
        downloader.download_submissions(
            submission_type=['8-K'],
            filing_date=(date_str, date_str),  # Same date for start and end to get single day
            output_dir=f'8-K/{month:02d}/{day:02d}'
        )

print("Downloading Form 4")
for month in range(1, 13):
   start = f'2024-{month:02d}-01'
   end = f'2024-{month:02d}-31'
   downloader = PremiumDownloader()
   downloader.download_submissions(submission_type=['4'], filing_date=(start, end),output_dir=f'4/{month:02d}')
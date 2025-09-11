from datamule import Portfolio
import calendar
import csv
import os
from tqdm import tqdm

# CODE TO CONSTRUCT FISCAL YEAR ENDS
# THIS GETS CHANGES OVER TIME

def safe_get(data, key, default=None):
    """Safely get value from dict. If value is a list, return first item."""
    try:
        value = data[key]
        return value[0] if isinstance(value, list) and len(value) > 0 else value
    except (KeyError, IndexError, TypeError):
        return default

# fiscal year end
fiscal_year_end_dir = "10k_fiscal_year_end"

# DIRECTORY THAT CONTAINS EACH PORTFOLIO #
portfolio_master_dir = 'test'

# SET FOR TESTING PURPOSES #
# CHANGE TO 1994 to present day # 
start_year = 2001
current_year = 2001
current_month = 2

os.makedirs(fiscal_year_end_dir, exist_ok=True)

# DOWNLOAD #
for year in range(start_year, current_year + 1):
    start_month = 1 if year > start_year else 1
    end_month = 12 if year < current_year else current_month
    
    for month in range(start_month, end_month + 1):
        portfolio = Portfolio(f'{portfolio_master_dir}/{year}_{month:02d}')

        # What filings to download
        submission_types = ['10-K','10-K/A']

        # What documents within filings to download
        document_types = ['10-K','10-K/A']

        # Calculate first and last day of the month
        first_day = f"{year}-{month:02d}-01"
        last_day = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"

        print(f"Downloading filings for {year}-{month:02d}: {first_day} to {last_day}")
        
        portfolio.download_submissions(
            submission_type=submission_types,
            filing_date=(first_day, last_day),
            document_type=[], # Change this to document types to only download 10-K root forms
            provider = 'datamule' # Uses the datamule provider
        )

# GET fiscalYearEnd #
for year in range(start_year, current_year + 1):
    start_month = 1 if year > start_year else 1
    end_month = 12 if year < current_year else current_month
    
    for month in range(start_month, end_month + 1):
        portfolio = Portfolio(f'{portfolio_master_dir}/{year}_{month:02d}')

        fiscal_year_end_list = []

        # create directory for month
        month_dir = f"{fiscal_year_end_dir}/{year}/{month}"
        os.makedirs(month_dir, exist_ok=True)
        
        for submission in tqdm(portfolio, total=None, desc=f"Processing {year}-{month:02d}"):
            try:
                metadata = submission.metadata.content
                accession = safe_get(metadata, 'accession-number')
                
                # Handle both single filer (dict) and multiple filers (list)
                filer_data = metadata.get('filer')
                
                if isinstance(filer_data, list):
                    # Multiple filers - process each one
                    for filer in filer_data:
                        company_data = filer.get('company-data', {})
                        cik = safe_get(company_data, 'cik')
                        fiscal_year_end = safe_get(company_data, 'fiscal-year-end')
                        
                        if accession and cik and fiscal_year_end:
                            fiscal_year_end_list.append((accession, cik, fiscal_year_end))
                            
                elif isinstance(filer_data, dict):
                    # Single filer - process it
                    company_data = filer_data.get('company-data', {})
                    cik = safe_get(company_data, 'cik')
                    fiscal_year_end = safe_get(company_data, 'fiscal-year-end')
                    
                    if accession and cik and fiscal_year_end:
                        fiscal_year_end_list.append((accession, cik, fiscal_year_end))
                        
            except Exception as e:
                print(f"Error processing submission: {e}. Note: expect quite a few of these, especially in early years. The culprit is likely malformed SGML files on the SEC side.")
        
        # write to csv
        csv_filename = f"{month_dir}/fiscal_year_end_{year}_{month:02d}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            
            # Write header row
            csv_writer.writerow(['accession_number', 'cik', 'fiscal_year_end'])
            
            # Write data rows
            csv_writer.writerows(fiscal_year_end_list)
        

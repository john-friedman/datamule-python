from datetime import datetime, timedelta
import pkg_resources
import io
import re
import os
import zipfile
import csv
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def process_ftd_zip(zip_path):
    """
    Process a single FTD (Fails-to-Deliver) ZIP file by converting its contents to CSV format.

    This function extracts the contents of a ZIP file containing tab-delimited data,
    converts it to CSV format, and removes the original ZIP file.

    Parameters
    ----------
    zip_path : str
        Path to the ZIP file to process

    Notes
    -----
    - Assumes each ZIP file contains exactly one data file
    - Uses '|' as the delimiter for input data
    - Removes the original ZIP file after processing
    - Handles UTF-8 encoding with replacement for invalid characters

    Examples
    --------
    >>> process_ftd_zip('path/to/cnsfails202301a.zip')
    """
    base_name = os.path.splitext(zip_path)[0]
    csv_path = f"{base_name}.csv"
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_name = zip_ref.namelist()[0]  # Assuming only one file per zip
        with zip_ref.open(file_name) as file:
            content = io.TextIOWrapper(file, encoding='utf-8', errors='replace').read()
    
    # Convert tab-delimited content to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for line in content.split('\n'):
            writer.writerow(line.split('|'))
    
    # Remove the original zip file
    os.remove(zip_path)

def process_all_ftd_zips(output_dir):
    """
    Process all FTD ZIP files in a directory concurrently.

    Uses ThreadPoolExecutor for parallel processing with progress tracking.

    Parameters
    ----------
    output_dir : str
        Directory containing the ZIP files to process

    Notes
    -----
    - Processes all files ending with '.zip' in the directory
    - Shows progress bar during processing
    - Uses system default number of worker threads

    Examples
    --------
    >>> process_all_ftd_zips('/path/to/ftd/files')
    """
    zip_files = [f for f in os.listdir(output_dir) if f.endswith('.zip')]
    
    # Use ThreadPoolExecutor for parallel processing with tqdm
    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(lambda f: process_ftd_zip(os.path.join(output_dir, f)), zip_files),
                  total=len(zip_files),
                  desc="Processing ZIP files",
                  unit="file"))

def load_csv_data():
    """
    Load existing FTD locations data from the package's data directory.

    Returns
    -------
    list of dict
        List of dictionaries containing the CSV data, where each dictionary
        represents a row with keys from the CSV header

    Notes
    -----
    - Reads from 'ftd_locations.csv' in the package's data directory
    - Uses UTF-8 encoding
    - Assumes CSV has a header row

    Examples
    --------
    >>> data = load_csv_data()
    >>> print(data[0]['url'])  # Print first URL in data
    """
    csv_content = pkg_resources.resource_string('datamule', 'data/ftd_locations.csv')
    csv_data = []
    csv_file = io.StringIO(csv_content.decode('utf-8'))
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        csv_data.append(row)
    return csv_data

def extract_date_from_url(url):
    """
    Extract the date from an FTD file URL.

    Parameters
    ----------
    url : str
        URL of the FTD file

    Returns
    -------
    datetime or None
        Datetime object representing the month and year from the URL,
        or None if no date is found

    Notes
    -----
    - Expects URLs in format containing 'cnsfails{YYYYMM}[a|b].zip'
    - Returns None if the URL doesn't match the expected pattern

    Examples
    --------
    >>> url = "https://www.sec.gov/files/data/fails-deliver-data/cnsfails202301a.zip"
    >>> date = extract_date_from_url(url)
    >>> print(date)
    2023-01-01 00:00:00
    """
    match = re.search(r'cnsfails(\d{6})[ab]\.zip', url)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, '%Y%m')
    return None

def generate_urls(start_date, end_date):
    """
    Generate FTD file URLs for a date range.

    Parameters
    ----------
    start_date : datetime
        Start date for URL generation
    end_date : datetime
        End date for URL generation

    Returns
    -------
    list of str
        List of URLs for FTD files in the date range

    Notes
    -----
    - Generates two URLs per month ('a' and 'b' files)
    - Uses 15-day intervals for half-month periods
    - URLs follow SEC's file naming convention

    Examples
    --------
    >>> start = datetime(2023, 1, 1)
    >>> end = datetime(2023, 12, 31)
    >>> urls = generate_urls(start, end)
    """
    urls = []
    current_date = start_date
    while current_date <= end_date:
        for half in ['a', 'b']:
            url = f"https://www.sec.gov/files/data/fails-deliver-data/cnsfails{current_date.strftime('%Y%m')}{half}.zip"
            urls.append(url)
        current_date += timedelta(days=15)  # Move to the next half-month
    return urls

def get_all_ftd_urls():
    """
    Get a complete list of FTD URLs, including both existing and new ones.

    Returns
    -------
    list of str
        Combined list of existing and newly generated URLs

    Notes
    -----
    - Loads existing URLs from the package's data file
    - Finds the latest date in existing URLs
    - Generates new URLs from the month after the latest date up to current date
    - Combines and returns all URLs

    Examples
    --------
    >>> urls = get_all_ftd_urls()
    >>> print(len(urls))  # Number of URLs
    >>> print(urls[-1])   # Most recent URL
    """
    # Load existing URLs
    csv_data = load_csv_data()
    existing_urls = [row['url'] for row in csv_data]

    # Find the last date in the existing URLs
    last_date = max(extract_date_from_url(url) for url in existing_urls if extract_date_from_url(url))

    # Generate new URLs starting from the month after the last date
    start_date = (last_date.replace(day=1) + timedelta(days=32)).replace(day=1)
    end_date = datetime.now()
    
    new_urls = generate_urls(start_date, end_date)

    # Combine and return all URLs
    return existing_urls + new_urls
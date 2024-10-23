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
    zip_files = [f for f in os.listdir(output_dir) if f.endswith('.zip')]
    
    # Use ThreadPoolExecutor for parallel processing with tqdm
    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(lambda f: process_ftd_zip(os.path.join(output_dir, f)), zip_files),
                  total=len(zip_files),
                  desc="Processing ZIP files",
                  unit="file"))

def load_csv_data():
    csv_content = pkg_resources.resource_string('datamule', 'data/ftd_locations.csv')
    csv_data = []
    csv_file = io.StringIO(csv_content.decode('utf-8'))
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        csv_data.append(row)
    return csv_data

def extract_date_from_url(url):
    match = re.search(r'cnsfails(\d{6})[ab]\.zip', url)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, '%Y%m')
    return None

def generate_urls(start_date, end_date):
    urls = []
    current_date = start_date
    while current_date <= end_date:
        for half in ['a', 'b']:
            url = f"https://www.sec.gov/files/data/fails-deliver-data/cnsfails{current_date.strftime('%Y%m')}{half}.zip"
            urls.append(url)
        current_date += timedelta(days=15)  # Move to the next half-month
    return urls

def get_all_ftd_urls():
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
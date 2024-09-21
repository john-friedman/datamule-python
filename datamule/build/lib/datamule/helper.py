import requests
import os
from tqdm import tqdm
import zipfile
from pkg_resources import resource_filename
import csv

# Unused in current implementation.
def construct_primary_doc_url(cik, accession_number,primary_doc_url):
    accession_number = accession_number.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{primary_doc_url}"

# DONE
def _download_from_dropbox(url, output_path):
    headers = {'user-agent': 'Wget/1.16 (linux-gnu)'}
    r = requests.get(url, stream=True, headers=headers)
    total_size = int(r.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as f, tqdm(
        desc="Downloading " + os.path.basename(output_path),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for chunk in r.iter_content(chunk_size=1024):
            size = f.write(chunk)
            progress_bar.update(size)
    
    # Check if the downloaded file is a zip file
    if zipfile.is_zipfile(output_path):
        extract_path = os.path.dirname(output_path)
        with zipfile.ZipFile(output_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                extract_file_path = os.path.join(extract_path, file_info.filename)
                with zip_ref.open(file_info) as file_in_zip, \
                    open(extract_file_path, 'wb') as output_file, \
                    tqdm(total=file_info.file_size, unit='B', unit_scale=True, 
                         desc=f"Extracting {file_info.filename}") as pbar:
                    while True:
                        chunk = file_in_zip.read(8192)
                        if not chunk:
                            break
                        output_file.write(chunk)
                        pbar.update(len(chunk))
        
        # Remove the zip file after extraction
        os.remove(output_path)
        print(f"Extracted contents to {extract_path}")
    else:
        print(f"Downloaded file is not a zip. Saved to {output_path}")

# May generalize to load any package resource
def load_company_tickers():
    """Load company tickers from package"""
    csv_path = resource_filename('datamule', 'data/company_tickers.csv')
    company_tickers = []
    
    with open(csv_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            company_tickers.append(row)
    
    return company_tickers

# DONE
def identifier_to_cik(ticker):
    """Convert company tickers to CIK codes"""
    company_tickers = load_company_tickers()
    if ticker:
        if isinstance(ticker, list):
            cik = []
            for t in ticker:
                cik.extend([company['cik'] for company in company_tickers if t == company['ticker']])
        else:
            cik = [company['cik'] for company in company_tickers if ticker == company['ticker']]

    if not cik:
        raise ValueError("No matching companies found")

    return cik
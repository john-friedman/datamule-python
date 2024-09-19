import requests
import os
from tqdm import tqdm
import zipfile
import shutil
from pkg_resources import resource_filename
import csv

def construct_primary_doc_url(cik, accession_number,primary_doc_url):
    accession_number = accession_number.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{primary_doc_url}"

def _download_from_dropbox(url, output_path):
    headers = {'user-agent': 'Wget/1.16 (linux-gnu)'}
    r = requests.get(url, stream=True, headers=headers)
    total_size = int(r.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as f, tqdm(
        desc=output_path,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for chunk in r.iter_content(chunk_size=1024):
            size = f.write(chunk)
            progress_bar.update(size)


def load_company_tickers():
    csv_path = resource_filename('datamule', 'data/company_tickers.csv')
    company_tickers = []
    
    with open(csv_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            company_tickers.append(row)
    
    return company_tickers

def identifier_to_cik(ticker):
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
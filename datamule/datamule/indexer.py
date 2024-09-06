import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import pandas as pd
import time
from tqdm import tqdm
from datetime import datetime
import csv
import os
from global_vars import headers
import requests
import json

class SECIndexer:
    API_BASE_URL = "https://data.sec.gov/submissions/"
    HEADERS = headers

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.tickers_file = os.path.join(data_dir, "company_tickers.csv")
        self.filings_file = os.path.join(data_dir, "filings_index.csv")
        self.submissions_file = os.path.join(data_dir, "submissions_index.csv")
        os.makedirs(data_dir, exist_ok=True)

    def get_company_tickers(self, force_refresh=False):
            if not force_refresh and os.path.exists(self.tickers_file):
                return pd.read_csv(self.tickers_file)
            
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.HEADERS)
            if response.status_code == 200:
                df = pd.DataFrame.from_dict(response.json(), orient='index')
                df.columns = ['cik', 'ticker', 'title']
                df['cik'] = df['cik'].astype(str).str.zfill(10)
                df.to_csv(self.tickers_file, index=False)
                return df
            else:
                raise Exception(f"Failed to fetch company tickers. Status code: {response.status_code}")

    async def fetch_json(self, session, url, limiter):
        try:
            async with limiter:
                async with session.get(url, headers=self.HEADERS) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Error fetching {url}: HTTP {response.status}")
        except Exception as e:
            print(f"Exception while fetching {url}: {str(e)}")
        return None

    def process_filing_data(self, data, cik):
        try:
            if 'filings' in data:
                recent = data['filings']['recent']
                filings = zip(recent['accessionNumber'], recent['filingDate'], recent['primaryDocument'], recent['form'])
                additional_files = data["filings"].get("files", [])
            else:
                filings = zip(data['accessionNumber'], data['filingDate'], data['primaryDocument'], data['form'])
                additional_files = []
            
            processed_filings = []
            processed_submissions = []
            
            for accession, date, url, form in filings:
                parts = accession.split('-')
                accession_parts = [int(part) for part in parts]
                processed_filings.append(tuple(accession_parts + [date, url]))
                processed_submissions.append(tuple(accession_parts + [form, cik]))
            
            return processed_filings, processed_submissions, additional_files
        except Exception as e:
            print(f"Error processing filing data: {str(e)}")
            return [], [], []

    def update_csv(self, data, output_file):
        mode = 'a' if os.path.exists(output_file) else 'w'
        try:
            with open(output_file, mode, newline='') as csvfile:
                writer = csv.writer(csvfile)
                if mode == 'w':
                    if 'filings_index.csv' in output_file:
                        writer.writerow(['filing_entity', 'accepted_year', 'filing_count', 'filing_date', 'primary_doc_url'])
                    elif 'submissions_index.csv' in output_file:
                        writer.writerow(['filing_entity', 'accepted_year', 'filing_count', 'form', 'cik'])
                writer.writerows(data)
        except Exception as e:
            print(f"Error in CSV update: {str(e)}")

    async def process_cik(self, session, cik, limiter):
        main_url = f"{self.API_BASE_URL}CIK{str(cik).zfill(10)}.json"
        processed_files = set()
        files_to_process = [main_url]
        
        while files_to_process:
            url = files_to_process.pop(0)
            if url in processed_files:
                continue
            
            data = await self.fetch_json(session, url, limiter)
            if not data:
                continue
            
            filings, submissions, additional_files = self.process_filing_data(data, cik)
            self.update_csv(filings, self.filings_file)
            self.update_csv(submissions, self.submissions_file)
            
            for file in additional_files:
                files_to_process.append(f"{self.API_BASE_URL}{file['name']}")
            
            processed_files.add(url)
        
        return len(processed_files)

    async def scrape_filings(self):
        limiter = AsyncLimiter(10, 1)  # 10 requests per second
        
        try:
            company_tickers = self.get_company_tickers()
            ciks = company_tickers['cik'].tolist()

            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                tasks = [self.process_cik(session, cik, limiter) for cik in ciks]
                results = []
                for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Processing CIKs"):
                    results.append(await f)
            end_time = time.time()

            total_files_processed = sum(results)
            print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
            print(f"Total files processed: {total_files_processed}")
        except Exception as e:
            print(f"An error occurred in the scraping process: {str(e)}")

    def run(self):
        print(f"Starting SEC filing scraper at {datetime.now()}")
        asyncio.run(self.scrape_filings())

def run():
    scraper = SECIndexer()
    scraper.run()

    # Load metadata.json if it exists, or create a new dictionary
    try:
        with open('data/metadata.json', 'r') as f:
            metadata = json.load(f)
    except FileNotFoundError:
        metadata = {}

    # Update the 'last_index_update' key with the current datetime
    metadata['last_index_update'] = datetime.now().isoformat()

    # Save the updated metadata back to the file
    with open('data/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)
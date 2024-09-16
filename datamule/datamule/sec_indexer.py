import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import time
from tqdm import tqdm
from datetime import datetime, timedelta
import csv
import os
from .global_vars import headers, indices_metadata_url, indices_company_tickers_url, indices_submissions_url
import requests
import json
import polars as pl
from .helper import _download_from_dropbox

class Indexer:
    def __init__(self, indices_path="data"):
        self.indices_path = indices_path
        self.tickers_file = os.path.join(indices_path, "company_tickers.csv")
        self.submissions_file = os.path.join(indices_path, "submissions_index.csv")
        self.metadata_file = os.path.join(indices_path, "metadata.json")
        os.makedirs(indices_path, exist_ok=True)

        self.headers = headers
        self.api_base_url = "https://data.sec.gov/submissions/"
        self.WATCH_URL = "https://efts.sec.gov/LATEST/search-index"

    def set_indices_path(self, indices_path):
        self.indices_path = indices_path

    def get_company_tickers(self, force_refresh=False):
        if not force_refresh and os.path.exists(self.tickers_file):
            return pl.read_csv(self.tickers_file)
        
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            # Parse the JSON content
            data = json.loads(response.content)
            # Convert the data to a list of dictionaries
            records = [
                    {
                        "cik": str(v["cik_str"]).zfill(10),
                        "ticker": v["ticker"],
                        "title": v["title"]
                    }
                    for _, v in data.items()
            ]
            
            # Create a Polars DataFrame
            df = pl.DataFrame(records)
            df.write_csv(self.tickers_file)
            print(f"Company tickers saved to {self.tickers_file}")
            return df
        else:
            raise Exception(f"Failed to fetch company tickers. Status code: {response.status_code}")
            

    async def fetch_json(self, session, url, limiter):
        try:
            async with limiter:
                async with session.get(url, headers=self.headers) as response:
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
            
            processed_data = []
            
            for accession, date, url, form in filings:
                processed_data.append(tuple([accession, date, url, form, cik]))
            
            return processed_data, additional_files
        except Exception as e:
            print(f"Error processing filing data: {str(e)}")
            return [], []

    def update_csv(self, data, output_file):
        mode = 'a' if os.path.exists(output_file) else 'w'
        try:
            with open(output_file, mode, newline='') as csvfile:
                writer = csv.writer(csvfile)
                if mode == 'w':
                    writer.writerow(['accession_number', 'filing_date', 'primary_doc_url', 'form', 'cik'])
                writer.writerows(data)
        except Exception as e:
            print(f"Error in CSV update: {str(e)}")

    async def process_cik(self, session, cik, limiter):
        main_url = f"{self.api_base_url}CIK{str(cik).zfill(10)}.json"
        processed_files = set()
        files_to_process = [main_url]
        
        while files_to_process:
            url = files_to_process.pop(0)
            if url in processed_files:
                continue
            
            data = await self.fetch_json(session, url, limiter)
            if not data:
                continue
            
            processed_data, additional_files = self.process_filing_data(data, cik)
            self.update_csv(processed_data, self.submissions_file)
            
            for file in additional_files:
                files_to_process.append(f"{self.api_base_url}{file['name']}")
            
            processed_files.add(url)
        
        return len(processed_files)

    async def scrape_filings(self):
        limiter = AsyncLimiter(10, 1)  # 10 requests per second
        
        try:
            company_tickers = self.get_company_tickers()
            ciks = company_tickers['cik'].to_list()

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

    def run(self,download=True):

        if download:
            print(f"Downloading indices at {datetime.now()}")
            os.makedirs(self.indices_path, exist_ok=True)
            _download_from_dropbox(indices_metadata_url, self.metadata_file)
            _download_from_dropbox(indices_company_tickers_url, self.tickers_file)
            _download_from_dropbox(indices_submissions_url, self.submissions_file)
        else:
            print(f"Starting SEC Indexer at {datetime.now()}")
            asyncio.run(self.scrape_filings())

            # Load metadata.json if it exists, or create a new dictionary
            try:
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
            except FileNotFoundError:
                metadata = {}

            # Update the 'last_index_update' key with the current datetime
            metadata['last_index_update'] = datetime.now().isoformat()

            # Save the updated metadata back to the file
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)

    async def _watch_efts(self, form=None, cik=None, interval=1, silent=False):
        params = {
            "startdt": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "enddt": datetime.now().strftime("%Y-%m-%d")
        }

        # Handle forms parameter
        if form:
            if isinstance(form, str):
                params["forms"] = form
            elif isinstance(form, list):
                params["forms"] = ",".join(form)
            else:
                raise ValueError("forms must be a string or a list of strings")
        else:
            params["forms"] = "-0"  # Default value if no forms specified

        # Handle cik parameter
        if cik:
            if isinstance(cik, str):
                params["ciks"] = cik
            elif isinstance(cik, list):
                params["ciks"] = ",".join(cik)
            else:
                raise ValueError("cik must be a string or a list of strings")

        previous_value = None
        
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.get(self.WATCH_URL, params=params, headers=self.headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            current_value = data['hits']['total']['value']
                            
                            if previous_value is not None and current_value != previous_value:
                                if not silent:
                                    print(f"Value changed from {previous_value} to {current_value}")
                                return True
                            
                            previous_value = current_value
                            if not silent:
                                print(f"Current value: {current_value}. Checking again in {interval} seconds.")
                        else:
                            print(f"Error occurred: HTTP {response.status}")
                
                except aiohttp.ClientError as e:
                    print(f"Error occurred: {e}")
                
                await asyncio.sleep(interval)

    def watch(self,interval=1,silent=True,form=None,cik=None):
        return asyncio.run(self._watch_efts(interval=interval,silent=silent,form=form,cik=cik))
import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import random
import os
from .global_vars import headers
import pandas as pd
from helper import construct_primary_doc_url
from tqdm import tqdm
import json

class Downloader:
    def __init__(self, rate_limit=10):
        self.rate_limit = rate_limit
        self.limiter = AsyncLimiter(rate_limit, 1)  # rate_limit requests per second
        self.headers = headers
        self.filings_index = None
        self.submissions_index = None
        self.company_tickers = None
        self.last_index_update = None

        self.indices_path = 'data'

    def set_indices_path(self, indices_path):
        self.indices_path = indices_path

    def set_headers(self, headers):
        self.headers = headers

    async def _download_url(self, session, url, output_dir):
        max_retries = 5
        base_delay = 5

        filename = url.split('/')[-1]
        filepath = os.path.join(output_dir, filename)

        for attempt in range(max_retries):
            try:
                async with self.limiter:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 429:  # Too Many Requests
                            raise aiohttp.ClientResponseError(response.request_info, response.history, status=429)
                        content = await response.read()

                with open(filepath, 'wb') as f:
                    f.write(content)
            
                return filepath

            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limited. Retrying {url} in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    print(f"Error downloading {url}: {str(e)}")
                    return None
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")
                return None

        print(f"Max retries reached for {url}")
        return None

    async def _download_urls(self, urls, output_dir):
            os.makedirs(output_dir, exist_ok=True)

            async with aiohttp.ClientSession() as session:
                tasks = []
                for url in urls:
                    task = asyncio.create_task(self._download_url(session, url, output_dir))
                    tasks.append(task)

                results = []
                for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading files"):
                    result = await f
                    results.append(result)

            successful_downloads = [result for result in results if result is not None]
            print(f"Successfully downloaded {len(successful_downloads)} out of {len(urls)} URLs")
            return successful_downloads

    def run_download_urls(self, urls, output_dir='data'):
        return asyncio.run(self._download_urls(urls, output_dir))
    
    def _load_data(self):
        if any(x is None for x in [self.filings_index, self.submissions_index, self.company_tickers]):
            # load metadata json
            with open(self.indices_path + '/' + 'metadata.json', 'r') as f:
                metadata = json.load(f)
            last_index_update = metadata["last_index_update"]
            self.last_index_update = last_index_update
            print(f'Index last updated: {last_index_update}')


        if self.filings_index is None:
            print('Loading filings_index.csv')
            self.filings_index = pd.read_csv(self.indices_path + '/' + 'filings_index.csv')
        if self.submissions_index is None:
            print('Loading submissions_index.csv')
            self.submissions_index = pd.read_csv(self.indices_path + '/' + 'submissions_index.csv')
        if self.company_tickers is None:
            print('Loading company_tickers.csv')
            self.company_tickers = pd.read_csv(self.indices_path + '/' + 'company_tickers.csv')

    def download(self, output_dir='filings', form=None, date=None, cik=None, name=None, ticker=None):
        # Load data if not already loaded
        self._load_data()

        # Check there is only one identifier
        if sum(x is not None for x in [cik, name, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik, name, or ticker')

        # Filter submissions_index first (usually smaller than filings_index)
        submissions_mask = pd.Series(True, index=self.submissions_index.index)

        if form:
            form_list = [form] if isinstance(form, str) else form
            submissions_mask &= self.submissions_index['form'].isin(form_list)

        if cik:
            ciks = [int(c) for c in (cik if isinstance(cik, list) else [cik])]
            submissions_mask &= self.submissions_index['cik'].isin(ciks)

        if name or ticker:
            if name:
                matched_companies = self.company_tickers[self.company_tickers['title'].str.contains(name, case=False)]
            else:  # ticker
                tickers = [t.upper() for t in (ticker if isinstance(ticker, list) else [ticker])]
                matched_companies = self.company_tickers[self.company_tickers['ticker'].isin(tickers)]
            
            ciks = matched_companies['cik'].tolist()
            submissions_mask &= self.submissions_index['cik'].isin(ciks)

        filtered_submissions = self.submissions_index[submissions_mask]

        # Filter filings_index
        filings_mask = pd.Series(True, index=self.filings_index.index)

        if date:
            if isinstance(date, tuple) and len(date) == 2:
                start_date, end_date = date
                filings_mask &= (self.filings_index['filing_date'] >= start_date) & (self.filings_index['filing_date'] <= end_date)
            elif isinstance(date, list):
                filings_mask &= self.filings_index['filing_date'].isin(date)
            else:
                filings_mask &= (self.filings_index['filing_date'] == date)

        filtered_filings = self.filings_index[filings_mask]

        # Combine filters and merge with submissions to get CIK
        key_cols = ['filing_entity', 'accepted_year', 'filing_count']
        final_filings = pd.merge(
            filtered_filings,
            filtered_submissions[key_cols + ['cik']],
            on=key_cols,
            how='inner'
        )

        # Generate primary_doc_urls using construct_primary_doc_url function
        primary_doc_urls = final_filings.apply(
            lambda row: construct_primary_doc_url(
                row['cik'], row['filing_entity'], row['accepted_year'], 
                row['filing_count'], row['primary_doc_url']
            ), 
            axis=1
        ).tolist()

        # Download all primary_doc_urls
        print(f"Found {len(primary_doc_urls)} documents to download.")
        self.run_download_urls(primary_doc_urls, output_dir)
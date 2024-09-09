import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import random
import os
from .global_vars import headers
import pandas as pd
from .helper import construct_primary_doc_url, query_datamule_api, construct_primary_doc_url_from_cik_and_accession_number
from tqdm import tqdm
import json
import polars as pl
from time import time
import requests


class Downloader:
    def __init__(self, rate_limit=10):
        self.rate_limit = rate_limit
        self.limiter = AsyncLimiter(rate_limit, 1)  # rate_limit requests per second
        self.headers = headers
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
    
    # change to if no data found, ask to run index
    # load metadata and print last_index_update
    # load submissions_index
    # load company_tickers

    def _load_company_tickers(self):
        try:
            self.company_tickers = pl.read_csv(self.indices_path + '/company_tickers.csv')
        except FileNotFoundError as e:
            print('No company tickers found. Downloading company tickers...')
            
    def _load_indices(self):
        s = time()
        # load metadata
        try:
            with open(self.indices_path + '/metadata.json', 'r') as f:
                metadata = json.load(f)
                self.last_index_update = metadata.get('last_index_update')
        except FileNotFoundError as e:
            print('No metadata found. Use download_from_router or run the indexer to download the latest data.')
            return e
        
        # load submissions_index
        try:
            self.submissions_index = pl.read_csv(self.indices_path + '/submissions_index.csv')
        except FileNotFoundError as e:
            print('No submissions index found. Use download_from_router or run the indexer to download the latest data')
            return e
    
        print(f"Time to load data: {time() - s}")


    def download_from_router(self, output_dir='filings', form=None, date=None, cik=None, name=None, ticker=None):
        """Function to download filings without indices using SEC Router. Limit 10 responses per query. If you need bulk data, use the download function instead."""
        # first from ticker and name, get cik from self.company_tickers
        
        ciks = self.company_tickers.filter(pl.col('ticker').is_in(ticker))['cik'].to_list()
        ciks += self.company_tickers.filter(pl.col('title').str.contains(name, ignore_case=True))['cik'].to_list()
        dict_list = query_datamule_api(cik=ciks, form=form, date_range=date, output_dir=output_dir)

        # construct primary_doc_url from cik and accession_number
        primary_doc_urls = [construct_primary_doc_url_from_cik_and_accession_number(d['cik'], d['accession_number'], d['primary_doc_url']) for d in dict_list]
        # download filings
        self.run_download_urls(primary_doc_urls, output_dir)

        

    def download(self, output_dir='filings', form=None, date=None, cik=None, name=None, ticker=None):
        # Load data if not already loaded
        self._load_company_tickers()
        self._load_indices()

        # Check there is only one identifier
        if sum(x is not None for x in [cik, name, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik, name, or ticker')

        submissions_mask = pl.Series([True] * len(self.submissions_index))

        if form:
            form_list = [form] if isinstance(form, str) else form
            submissions_mask = submissions_mask & self.submissions_index['form'].is_in(form_list)

        if cik:
            ciks = [int(c) for c in (cik if isinstance(cik, list) else [cik])]
            submissions_mask = submissions_mask & self.submissions_index['cik'].is_in(ciks)

        if name or ticker:
            if name:
                matched_companies = self.company_tickers.filter(
                    pl.col('title').str.contains(name, ignore_case=True)
                )
            else:  # ticker
                tickers = [t.upper() for t in (ticker if isinstance(ticker, list) else [ticker])]
                matched_companies = self.company_tickers.filter(pl.col('ticker').is_in(tickers))
            
            ciks = matched_companies['cik'].to_list()
            submissions_mask = submissions_mask & self.submissions_index['cik'].is_in(ciks)

        filtered_submissions = self.submissions_index.filter(submissions_mask)

        # Generate primary_doc_urls using construct_primary_doc_url function
        primary_doc_urls = filtered_submissions.select(
            pl.struct(['cik', 'filing_entity', 'accepted_year', 'filing_count', 'primary_doc_url'])
            .map_elements(
                lambda row: construct_primary_doc_url(
                    row['cik'],
                    row['filing_entity'],
                    row['accepted_year'],
                    row['filing_count'],
                    row['primary_doc_url']
                ),
                return_dtype=pl.Utf8  # Assuming the URL is a string
            )
        ).to_series().to_list()

        # make sure all urls are unique, since multiple companies might have same submission
        primary_doc_urls = list(set(primary_doc_urls))

        # Download all primary_doc_urls
        print(f"Found {len(primary_doc_urls)} documents to download.")
        self.run_download_urls(primary_doc_urls, output_dir)
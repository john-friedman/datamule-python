import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import random
import os
from .global_vars import headers, dataset_10k_url, dataset_mda_url
from .helper import construct_primary_doc_url, _download_from_dropbox
from tqdm import tqdm
import json
import polars as pl
from time import time
import requests
import zipfile

class Downloader:
    def __init__(self, rate_limit=10):
        self.rate_limit = rate_limit
        self.limiter = AsyncLimiter(rate_limit, 1)  # rate_limit requests per second
        self.headers = headers
        self.submissions_index = None
        self.company_tickers = None
        self.last_index_update = None

        self.dataset_path = 'datasets'
        self.indices_path = 'data'

    def set_indices_path(self, indices_path):
        self.indices_path = indices_path

    def set_dataset_path(self, dataset_path):
        self.dataset_path = dataset_path

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
        # first check if urls are valid, e.g. have end extension
        urls = [url for url in urls if url.split('/')[-1].split('.')[-1] != '']
        
        return asyncio.run(self._download_urls(urls, output_dir))
    
    # change to if no data found, ask to run index
    # load metadata and print last_index_update
    # load submissions_index
    # load company_tickers

    def _load_company_tickers(self):
        try:
            self.company_tickers = pl.read_csv(self.indices_path + '/company_tickers.csv')
        except FileNotFoundError as e:
            raise FileNotFoundError('No company tickers found. Use download_using_api or run the indexer to download the latest data.')
            
    def _load_indices(self):
        s = time()
        # load metadata
        try:
            with open(self.indices_path + '/metadata.json', 'r') as f:
                metadata = json.load(f)
                self.last_index_update = metadata.get('last_index_update')
        except FileNotFoundError as e:
            raise FileNotFoundError('No metadata found. Use download_using_api or run the indexer to download the latest data.')
        
        # load submissions_index
        try:
            self.submissions_index = pl.read_csv(self.indices_path + '/submissions_index.csv')
        except FileNotFoundError as e:
            raise FileNotFoundError('No submissions index found. Use download_using_api or run the indexer to download the latest data.')
    
        print(f"Time to load data: {time() - s}")        

    def download(self, output_dir='filings',return_urls = False, form=None, date=None, cik=None, name=None, ticker=None):
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

        if date:
            if isinstance(date, tuple) and len(date) == 2:
                # Date range
                start_date, end_date = date
                submissions_mask = submissions_mask & (
                    (self.submissions_index['filing_date'] >= start_date) &
                    (self.submissions_index['filing_date'] <= end_date)
                )
            elif isinstance(date, list):
                # List of specific dates
                submissions_mask = submissions_mask & self.submissions_index['filing_date'].is_in(date)
            else:
                # Single date
                submissions_mask = submissions_mask & (self.submissions_index['filing_date'] == date)


        filtered_submissions = self.submissions_index.filter(submissions_mask)

        # Generate primary_doc_urls using construct_primary_doc_url function
        primary_doc_urls = filtered_submissions.select(
            pl.struct(['cik', 'accession_number', 'primary_doc_url'])
            .map_elements(
                lambda row: construct_primary_doc_url(
                    row['cik'],
                    row['accession_number'],
                    row['primary_doc_url']
                ),
                return_dtype=pl.Utf8  # Assuming the URL is a string
            )
        ).to_series().to_list()

        # make sure all urls are unique, since multiple companies might have same submission
        primary_doc_urls = list(set(primary_doc_urls))

        if return_urls:
            return primary_doc_urls

        # Download all primary_doc_urls
        print(f"Found {len(primary_doc_urls)} documents to download.")
        self.run_download_urls(primary_doc_urls, output_dir)

    def download_using_api(self, output_dir='filings', return_urls=False, **kwargs):
        base_url = "https://api.datamule.xyz/submissions"
        
        # Handle 'date' parameter
        if 'date' in kwargs:
            if isinstance(kwargs['date'], tuple):
                # If 'date' is a tuple, use it for date_range
                kwargs['date_range'] = ','.join(map(str, kwargs['date']))
            else:
                # If 'date' is a list or singular value, use it for filing_date
                if isinstance(kwargs['date'], list):
                    kwargs['filing_date'] = ','.join(map(str, kwargs['date']))
                else:
                    kwargs['filing_date'] = str(kwargs['date'])
            del kwargs['date']
        
        # Convert date_range to comma-separated string if it's a list
        if 'date_range' in kwargs and isinstance(kwargs['date_range'], list):
            kwargs['date_range'] = ','.join(map(str, kwargs['date_range']))
        
        # Convert filing_date to comma-separated string if it's a list
        if 'filing_date' in kwargs and isinstance(kwargs['filing_date'], list):
            kwargs['filing_date'] = ','.join(map(str, kwargs['filing_date']))
        
        response = requests.get(base_url, params=kwargs)
        response.raise_for_status()  # Raise an exception for HTTP errors

        dict_list = response.json()
        # construct primary_doc_url from cik and accession_number
        primary_doc_urls = [construct_primary_doc_url(d['cik'], d['accession_number'], d['primary_doc_url']) for d in dict_list]
        if return_urls:
            return primary_doc_urls
        # download filings
        self.run_download_urls(primary_doc_urls, output_dir)
        return response.json()
    
    def download_dataset(self,dataset):
        # check if dataset dir exists
        if not os.path.exists(self.dataset_path):
            os.makedirs(self.dataset_path)

        if dataset == '10K':
            zip_path = self.dataset_path + '/10K.zip'
            extract_path = self.dataset_path
            _download_from_dropbox(dataset_10k_url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # delete zip file
            os.remove(zip_path)
        elif dataset == "MDA":
            zip_path = self.dataset_path + '/MDA.zip'
            extract_path = self.dataset_path + '/MDA.csv'
            _download_from_dropbox(dataset_mda_url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get the info of the only file in the zip
                file_info = zip_ref.infolist()[0]
                
                # Open the file within the zip
                with zip_ref.open(file_info) as file_in_zip, \
                    open(extract_path, 'wb') as output_file:
                    
                    # Setup the progress bar
                    with tqdm(total=file_info.file_size, unit='B', unit_scale=True, desc="Extracting") as pbar:
                        while True:
                            chunk = file_in_zip.read(8192)  # Read in 8KB chunks
                            if not chunk:
                                break
                            output_file.write(chunk)
                            pbar.update(len(chunk))

            # delete zip file
            os.remove(zip_path)
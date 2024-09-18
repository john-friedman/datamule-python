import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import random
import os
from .global_vars import headers, dataset_10k_url, dataset_mda_url
from .helper import construct_primary_doc_url, _download_from_dropbox
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
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

        self.dataset_path = 'datasets'

    def set_dataset_path(self, dataset_path):
        self.dataset_path = dataset_path

    def set_headers(self, headers):
        self.headers = headers

    # Downloads a filing's primary document from the SEC website
    async def _download_url(self, session, url, output_dir):
        max_retries = 5
        base_delay = 5

        filename = url.split('/')[7] + url.split('/')[-1]
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

    # Downloads a list of URLs to a specified directory
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

    # Runs the downloads
    def run_download_urls(self, urls, output_dir='filings'):
        # first check if urls are valid, e.g. have end extension
        urls = [url for url in urls if url.split('/')[-1].split('.')[-1] != '']
        
        return asyncio.run(self._download_urls(urls, output_dir))
    
    def download(self, output_dir='filings',return_urls = False, form=None, date=None, cik=None, name=None, ticker=None):
        """return_urls: if True, returns a list of URLs to download. If False, downloads the files to output_dir."""
        # Note: we removed human_readable since the EFTS API does not have it. If people want it back, we can add it back in since each form has a speicifc URL that can be used to download the human readable version.
        # load company tickers

        # name / ticker will be converted to CIK. We will need to find more company names. currently only have ones with tickers.

        # Check there is only one identifier
        if sum(x is not None for x in [cik, name, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik, name, or ticker')
        

        # if form we add to params. making sure to modify search to only vary dates

        # if date we add to params. making sure we only download within that date range.

        # combos
        form, cik, date,   
     
    async def _fetch_url_for_efts(self,session, url, rate_limiter):
        async with rate_limiter:
            try:
                async with asyncio.timeout(10):  # 10 second timeout
                    async with session.get(url, headers=self.headers) as response:
                        #print(f"Requesting {url}")
                        if response.status != 200:
                            print(f"Error: HTTP {response.status}")
                            return None
                        return await response.json()
            except asyncio.TimeoutError:
                print(f"Timeout occurred for {url}")
            except Exception as e:
                print(f"Error occurred: {e}")
        return None

    async def _get_filing_urls_from_efts(self, base_url):
        rate_limiter = AsyncLimiter(10, 1)  # 10 requests per second
        full_urls = []
        start = 0
        page_size = 100

        async with aiohttp.ClientSession() as session:
            while True:
                tasks = []
                for i in range(10):  # Create 10 concurrent tasks
                    url = f"{base_url}&from={start + i * page_size}"
                    tasks.append(self._fetch_url_for_efts(session, url, rate_limiter))

                results = await atqdm.gather(*tasks, desc="Fetching URLs")
                
                for data in results:
                    if data is None or 'hits' not in data:
                        continue
                    
                    hits = data['hits']['hits']
                    
                    if not hits:
                        return full_urls  # All data fetched
                    
                    full_urls.extend([
                        f"https://www.sec.gov/Archives/edgar/data/{hit['_source']['ciks'][0]}/{hit['_id'].split(':')[0].replace('-', '')}/{hit['_id'].split(':')[1]}"
                        for hit in hits
                    ])
                    
                    if start + page_size > data['hits']['total']['value']:
                        return full_urls  # All data fetched
                
                start += 10 * page_size  # Move to the next batch

        return full_urls
    
    def _number_of_efts_filings(self,url):
        response = requests.get(url, headers=self.headers)
        data = response.json()

        doc_count = 0
        for bucket in data['aggregations']['form_filter']['buckets']:
            doc_count += bucket['doc_count']
        return doc_count
    
    def orchestrator(self, return_urls= False,cik=None, name= None, ticker = None, form = None, date = None):
        base_url = "https://efts.sec.gov/LATEST/search-index?"
        # convert name / ticker to CIK

        # Check there is only one identifier
        if sum(x is not None for x in [cik, name, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik, name, or ticker')
        
        # construct the EFTS URL

        if cik is None:
            pass
        else:
            if isinstance(cik, list):
                base_url += f"&ciks={','.join(cik)}"
            else:
                base_url += f"&ciks={cik}"

        if date is not None:
            if isinstance(date, str):
                base_url += f"&startdt={date}&enddt={date}"
        else:
            base_url += f"&startdt=2001-01-01&enddt={datetime.today().strftime('%Y-%m-%d')}"

        # if both date and form are none
        if form is None and date is None:
            pass
        else:
            if form is None:
                base_url += f"forms=-0" # all forms
            else:
                if isinstance(form, list):
                    base_url += f"&forms={','.join(form)}"
                else:
                    base_url += f"&forms={form}"

            total_filings = self._number_of_efts_filings(base_url)

            if total_filings < 10000:
                efts_urls = [base_url]
            else:
                pass

                # find total number of filings by sending one request
                # then subset by date to aggregate under 10000, aiming for 1,000

        all_primary_doc_urls = []
        for efts_url in efts_urls:
            # fetch the URLs from the EFTS API
            primary_doc_urls = asyncio.run(self._get_filing_urls_from_efts(efts_url))

            # remove duplicates (We should test this later) WIP
            primary_doc_urls = list(set(primary_doc_urls))

            if not return_urls:
                # download the filings
                self.run_download_urls(primary_doc_urls)
            else:
                all_primary_doc_urls.extend(primary_doc_urls)
        
        if return_urls:
            return all_primary_doc_urls

       
    
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

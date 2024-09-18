import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import random
import os
from .global_vars import headers, dataset_10k_url, dataset_mda_url
from .helper import _download_from_dropbox
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
import requests
import zipfile
from datetime import datetime
import math
from urllib.parse import urlparse, parse_qs, urlencode
from datetime import datetime, timedelta


class Downloader:
    def __init__(self, rate_limit=10):
        self.rate_limit = rate_limit
        self.global_limiter = AsyncLimiter(rate_limit, 1)  # global rate limiter
        self.headers = headers
        self.dataset_path = 'datasets'

    def set_dataset_path(self, dataset_path):
        self.dataset_path = dataset_path

    def set_headers(self, headers):
        self.headers = headers

    async def _download_url(self, session, url, output_dir):
        max_retries = 5
        base_delay = 5

        filename = url.split('/')[7] + '_' + url.split('/')[-1]
        filepath = os.path.join(output_dir, filename)

        for attempt in range(max_retries):
            try:
                async with self.global_limiter:  # Use global limiter
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 429:
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

    def run_download_urls(self, urls, output_dir='filings'):
        urls = [url for url in urls if url.split('/')[-1].split('.')[-1] != '']
        return asyncio.run(self._download_urls(urls, output_dir))
    
    async def _fetch_url_for_efts(self, session, url):
        async with self.global_limiter:  # Use global limiter
            try:
                async with asyncio.timeout(10):
                    async with session.get(url, headers=self.headers) as response:
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
        full_urls = []
        start = 0
        page_size = 100

        async with aiohttp.ClientSession() as session:
            while True:
                tasks = []
                for i in range(10):
                    url = f"{base_url}&from={start + i * page_size}"
                    tasks.append(self._fetch_url_for_efts(session, url))

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
    
    def _number_of_efts_filings(self, url):
        """Aggregates the number of filings from the EFTS API"""
        response = requests.get(url, headers=self.headers)
        data = response.json()

        doc_count = 0
        for bucket in data['aggregations']['form_filter']['buckets']:
            doc_count += bucket['doc_count']
        return doc_count
    

    def _subset_urls(self, full_url, total_filings, target_filings_per_range=1000):
        # Parse the URL
        parsed_url = urlparse(full_url)
        
        # Parse query parameters
        params = parse_qs(parsed_url.query)
        
        # Extract start and end dates
        start_date = params.get('startdt', [None])[0]
        end_date = params.get('enddt', [None])[0]

        if not start_date or not end_date:
            raise ValueError("Start date or end date not found in the URL")

        # Parse the start and end dates
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {e}")
        
        # Calculate the number of date ranges needed
        num_ranges = math.ceil(total_filings / target_filings_per_range)
        
        # Calculate the time delta for each range
        total_days = (end - start).days
        days_per_range = math.ceil(total_days / num_ranges)
        
        urls = []
        current_start = start
        
        for _ in range(num_ranges):
            current_end = min(current_start + timedelta(days=days_per_range), end)
            
            # Update query parameters
            new_params = params.copy()
            new_params['startdt'] = [current_start.strftime('%Y-%m-%d')]
            new_params['enddt'] = [current_end.strftime('%Y-%m-%d')]
            
            # Construct the new URL
            new_query = urlencode(new_params, doseq=True)
            new_url = parsed_url._replace(query=new_query).geturl()
            urls.append(new_url)
            
            if current_end == end:
                break
            
            current_start = current_end + timedelta(days=1)
        
        return urls
        
   
    
    def _conductor(self, efts_url, return_urls):
        """If the efts_url has more than 10,000 filings, it will subset the url into smaller chunks"""
        total_filings = self._number_of_efts_filings(efts_url)


        all_primary_doc_urls = []
        if total_filings < 10000:
            primary_doc_urls = asyncio.run(self._get_filing_urls_from_efts(efts_url))
            primary_doc_urls = list(set(primary_doc_urls))
            print(efts_url)
            print(f"Total filings: {len(primary_doc_urls)}")
            if not return_urls:
                self.run_download_urls(primary_doc_urls)
            else:
                all_primary_doc_urls.extend(primary_doc_urls)
        else:
            subset_urls = self._subset_urls(efts_url, total_filings)
            for subset_url in subset_urls:
                primary_doc_urls = asyncio.run(self._get_filing_urls_from_efts(subset_url))
                primary_doc_urls = list(set(primary_doc_urls))
                print(subset_url)
                print(f"Total filings: {len(primary_doc_urls)}")
                if not return_urls:
                    self.run_download_urls(primary_doc_urls)
                else:
                    all_primary_doc_urls.extend(primary_doc_urls)

        if return_urls:
            return all_primary_doc_urls
    
    def download(self, return_urls=False, cik=None, name=None, ticker=None, form=None, date=None):
        base_url = "https://efts.sec.gov/LATEST/search-index?"

        # setup name ticker to cik conversion
        # requires us to add company tickers as dependency
        
        if sum(x is not None for x in [cik, name, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik, name, or ticker')
        
        if cik is not None:
            if isinstance(cik, list):
                base_url += f"&ciks={','.join(cik)}"
            else:
                base_url += f"&ciks={cik}"

        if form is None:
            form_str = f"forms=-0"  # all forms
        else:
            if isinstance(form, list):
                form_str = f"&forms={','.join(form)}"
            else:
                form_str = f"&forms={form}"


        date_type = None # I think we need another function here to split
        if date is None:
            # Get filings starting from 2001
            date_str = f"&startdt=2001-01-01&enddt={datetime.now().strftime('%Y-%m-%d')}"
        elif isinstance(date, list): 
            date_type = 'list'
        elif isinstance(date, tuple):
            # date is a tuple of start and end dates
            date_str = f"&startdt={date[0]}&enddt={date[1]}"
        else:
            # date is a single date
            date_str = f"&startdt={date}&enddt={date}"

        if date_type == 'list':
            efts_url_list = [base_url + form_str + f"&startdt={d}&enddt={d}" for d in date]
        else:
            efts_url_list = [base_url + form_str + date_str]
            
        all_primary_doc_urls = []
        for efts_url in efts_url_list:
            # hand off to conductor, which downloads or returns urls
            if return_urls:
                primary_doc_urls = self._conductor(efts_url, True)
                all_primary_doc_urls.extend(primary_doc_urls)
            else:
                self._conductor(efts_url, False)
        
        if return_urls:
            return all_primary_doc_urls

    def download_dataset(self, dataset):
        if not os.path.exists(self.dataset_path):
            os.makedirs(self.dataset_path)

        if dataset == '10K':
            zip_path = self.dataset_path + '/10K.zip'
            extract_path = self.dataset_path
            _download_from_dropbox(dataset_10k_url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            os.remove(zip_path)
        elif dataset == "MDA":
            zip_path = self.dataset_path + '/MDA.zip'
            extract_path = self.dataset_path + '/MDA.csv'
            _download_from_dropbox(dataset_mda_url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_info = zip_ref.infolist()[0]
                with zip_ref.open(file_info) as file_in_zip, \
                    open(extract_path, 'wb') as output_file:
                    with tqdm(total=file_info.file_size, unit='B', unit_scale=True, desc="Extracting") as pbar:
                        while True:
                            chunk = file_in_zip.read(8192)
                            if not chunk:
                                break
                            output_file.write(chunk)
                            pbar.update(len(chunk))
            os.remove(zip_path)
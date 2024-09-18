import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import os
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
import requests
import zipfile
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode
import math
from .global_vars import headers
from pkg_resources import resource_filename
import csv

class Downloader:
    def __init__(self, rate_limit=10):
        self.global_limiter = AsyncLimiter(rate_limit, 1)
        self.headers = headers  # Define headers in global_vars.py
        self.dataset_path = 'datasets'

        self.company_tickers = self.load_company_tickers()

    def load_company_tickers(self):
        csv_path = resource_filename('datamule', 'data/company_tickers.csv')
        company_tickers = []
        
        with open(csv_path, 'r') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                company_tickers.append(row)
        
        return company_tickers


    async def _download_url(self, session, url, output_dir):
        filename = f"{url.split('/')[7]}_{url.split('/')[-1]}"
        filepath = os.path.join(output_dir, filename)

        for attempt in range(5):
            try:
                async with self.global_limiter:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 429:
                            raise aiohttp.ClientResponseError(response.request_info, response.history, status=429)
                        content = await response.read()
                
                with open(filepath, 'wb') as f:
                    f.write(content)
                return filepath
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    await asyncio.sleep(5 * (2 ** attempt) + 1)
                else:
                    print(f"Error downloading {url}: {str(e)}")
                    return None
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")
                return None
        return None

    async def _download_urls(self, urls, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            tasks = [self._download_url(session, url, output_dir) for url in urls]
            results = [await f for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading files")]
        successful_downloads = [result for result in results if result is not None]
        print(f"Successfully downloaded {len(successful_downloads)} out of {len(urls)} URLs")
        return successful_downloads

    def run_download_urls(self, urls, output_dir='filings'):
        return asyncio.run(self._download_urls([url for url in urls if url.split('/')[-1].split('.')[-1] != ''], output_dir))

    async def _fetch_url_for_efts(self, session, url):
        async with self.global_limiter:
            try:
                async with asyncio.timeout(10):
                    async with session.get(url, headers=self.headers) as response:
                        return await response.json() if response.status == 200 else None
            except Exception as e:
                print(f"Error occurred: {e}")
        return None

    async def _get_filing_urls_from_efts(self, base_url):
        full_urls = []
        start, page_size = 0, 100
        async with aiohttp.ClientSession() as session:
            while True:
                tasks = [self._fetch_url_for_efts(session, f"{base_url}&from={start + i * page_size}") for i in range(10)]
                results = await atqdm.gather(*tasks, desc="Fetching URLs")
                for data in results:
                    if data and 'hits' in data:
                        hits = data['hits']['hits']
                        if not hits:
                            return full_urls
                        full_urls.extend([f"https://www.sec.gov/Archives/edgar/data/{hit['_source']['ciks'][0]}/{hit['_id'].split(':')[0].replace('-', '')}/{hit['_id'].split(':')[1]}" for hit in hits])
                        if start + page_size > data['hits']['total']['value']:
                            return full_urls
                start += 10 * page_size
        return full_urls

    def _number_of_efts_filings(self, url):
        response = requests.get(url, headers=self.headers)
        return sum(bucket['doc_count'] for bucket in response.json()['aggregations']['form_filter']['buckets'])

    def _subset_urls(self, full_url, total_filings, target_filings_per_range=1000):
        parsed_url = urlparse(full_url)
        params = parse_qs(parsed_url.query)
        start = datetime.strptime(params.get('startdt', [None])[0], "%Y-%m-%d")
        end = datetime.strptime(params.get('enddt', [None])[0], "%Y-%m-%d")

        # If start and end dates are the same, modify forms
        if start == end:
            forms = params.get('forms', [None])[0]
            if forms == '-0':
                urls = []
                for form in ['SC 13G', 'SC 13G/A']:
                    new_params = params.copy()
                    new_params['forms'] = [form]
                    urls.append(parsed_url._replace(query=urlencode(new_params, doseq=True)).geturl())
                return urls
            else:
                # If forms is not '-0', return the original URL
                return [full_url]

        # If dates are different, proceed with the original logic
        num_ranges = math.ceil(total_filings / target_filings_per_range)
        days_per_range = math.ceil((end - start).days / num_ranges)
        
        urls = []
        current_start = start
        for _ in range(num_ranges):
            current_end = min(current_start + timedelta(days=days_per_range), end)
            new_params = params.copy()
            new_params['startdt'] = [current_start.strftime('%Y-%m-%d')]
            new_params['enddt'] = [current_end.strftime('%Y-%m-%d')]
            urls.append(parsed_url._replace(query=urlencode(new_params, doseq=True)).geturl())
            if current_end == end:
                break
            current_start = current_end + timedelta(days=1)
        return urls

    def _conductor(self, efts_url, return_urls):
        total_filings = self._number_of_efts_filings(efts_url)
        all_primary_doc_urls = []
        
        if total_filings < 10000:
            primary_doc_urls = asyncio.run(self._get_filing_urls_from_efts(efts_url))
            print(f"{efts_url}\nTotal filings: {len(primary_doc_urls)}")
            
            if return_urls:
                return primary_doc_urls
            else:
                self.run_download_urls(primary_doc_urls)
                return None
        
        for subset_url in self._subset_urls(efts_url, total_filings):
            sub_primary_doc_urls = self._conductor(subset_url, True)
            
            if return_urls:
                all_primary_doc_urls.extend(sub_primary_doc_urls)
            else:
                self.run_download_urls(sub_primary_doc_urls)
        
        return all_primary_doc_urls if return_urls else None

    def download(self, return_urls=False, cik=None, ticker=None, form=None, date=None):
        base_url = "https://efts.sec.gov/LATEST/search-index?"
        if sum(x is not None for x in [cik, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik, name, or ticker')
        
        if ticker is not None:
            cik = self._identifier_to_cik(ticker)
                
        if cik:
            if isinstance(cik, list):
                formatted_ciks = ','.join(str(c).zfill(10) for c in cik)
            else:
                formatted_ciks = str(cik).zfill(10)
            base_url += f"&ciks={formatted_ciks}"
        
        form_str = f"&forms={','.join(form) if isinstance(form, list) else form}" if form else "&forms=-0"
        
        if isinstance(date, list):
            efts_url_list = [f"{base_url}{form_str}&startdt={d}&enddt={d}" for d in date]
        else:
            date_str = f"&startdt={date}&enddt={date}" if date else f"&startdt=2001-01-01&enddt={datetime.now().strftime('%Y-%m-%d')}"
            efts_url_list = [f"{base_url}{form_str}{date_str}"]
        
        all_primary_doc_urls = []
        for efts_url in efts_url_list:
            if return_urls:
                all_primary_doc_urls.extend(self._conductor(efts_url, True))
            else:
                self._conductor(efts_url, False)
        
        return all_primary_doc_urls if return_urls else None

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


    async def _watch_efts(self, form=None, cik=None, interval=1, silent=False):
        params = {
            "startdt": (datetime.now()).strftime("%Y-%m-%d"),
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
            if isinstance(cik, list):
                params['ciks'] = ','.join(str(c).zfill(10) for c in cik)
        else:
            pass

        previous_value = None
        
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    watch_url = "https://efts.sec.gov/LATEST/search-index"
                    async with session.get(watch_url, params=params, headers=self.headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            if not silent:
                                print(response.url)
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

    # WIP add option to return new results
    def watch(self,interval=1,silent=True, form=None,cik=None, ticker=None):
        if sum(x is not None for x in [cik, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik, name, or ticker')
        
        if ticker:
            cik = self._identifier_to_cik(ticker)
        # wip add ticker conversion
        return asyncio.run(self._watch_efts(interval=interval,silent=silent,form=form,cik=cik))
    
    def _identifier_to_cik(self, ticker=None):
        if ticker:
            if isinstance(ticker, list):
                cik = []
                for t in ticker:
                    cik.extend([company['cik'] for company in self.company_tickers if t == company['ticker']])
            else:
                cik = [company['cik'] for company in self.company_tickers if ticker == company['ticker']]

        if not cik:
            raise ValueError("No matching companies found")

        return cik
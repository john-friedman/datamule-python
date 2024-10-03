import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import os
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode
import math
import re
import aiofiles
import json

from .global_vars import headers, dataset_10k_url, dataset_mda_url, dataset_xbrl_url, dataset_10k_record_list
from .helper import _download_from_dropbox, identifier_to_cik, load_company_tickers
from .zenodo_downloader import download_from_zenodo

class Downloader:
    def __init__(self):
        self.headers = headers
        self.dataset_path = 'datasets'
        self.domain_limiters = {
            'www.sec.gov': AsyncLimiter(7, 1),
            'efts.sec.gov': AsyncLimiter(10, 1),
            'default': AsyncLimiter(10, 1)
        }

    def set_limiter(self, domain, rate_limit):
        """Set a custom rate limit for a specific domain."""
        self.domain_limiters[domain] = AsyncLimiter(rate_limit, 1)

    def get_domain(self, url):
        """Extract the domain from a URL."""
        return urlparse(url).netloc

    def get_limiter(self, url):
        """Get the appropriate rate limiter for a given URL."""
        domain = self.get_domain(url)
        return self.domain_limiters.get(domain, self.domain_limiters['default'])

    async def _fetch_content_from_url(self, session, url, max_retries=3, current_retry=0):
        """Asynchronously fetch content from a URL with domain-specific rate limiting."""
        limiter = self.get_limiter(url)
        async with limiter:
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 429:
                        if current_retry >= max_retries:
                            raise Exception(f"Max retries ({max_retries}) exceeded for URL: {url}")
                        
                        retry_after = int(response.headers.get('Retry-After', 603))
                        print(f"Rate limited. Retry {current_retry + 1}/{max_retries} after {retry_after} seconds.")
                        await asyncio.sleep(retry_after)
                        return await self._fetch_content_from_url(session, url, max_retries, current_retry + 1)
                    
                    response.raise_for_status()
                    return await response.read()
            
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    if current_retry >= max_retries:
                        raise Exception(f"Max retries ({max_retries}) exceeded for URL: {url}")
                    
                    retry_after = int(e.headers.get('Retry-After', 603))
                    print(f"Rate limited. Retry {current_retry + 1}/{max_retries} after {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    return await self._fetch_content_from_url(session, url, max_retries, current_retry + 1)
                raise
            
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")
                if current_retry < max_retries:
                    print(f"Retrying ({current_retry + 1}/{max_retries})...")
                    await asyncio.sleep(5)  # Wait 5 seconds before retrying
                    return await self._fetch_content_from_url(session, url, max_retries, current_retry + 1)
                raise

    async def write_content_to_file(self, content, filepath):
        """Write content to a file asynchronously."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(content)

    def generate_url(self, base_url, params):
        """Generate a URL based on parameters."""
        return f"{base_url}?{urlencode(params)}"

    async def download_file(self, session, url, output_path):
        """Download a file from a URL and save it to the specified path."""
        content = await self._fetch_content_from_url(session, url)
        await self.write_content_to_file(content, output_path)
        return output_path

    async def _fetch_json_from_url(self, session, url):
        """Asynchronously fetch JSON data from a URL."""
        content = await self._fetch_content_from_url(session, url)
        return json.loads(content)

    async def _download_urls(self, urls, filenames, output_dir):
        """Asynchronously download a list of URLs to a specified directory."""
        os.makedirs(output_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            tasks = [self.download_file(session, url, os.path.join(output_dir, filename)) 
                     for url, filename in zip(urls, filenames) if filename]
            results = [await f for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading files")]
        successful_downloads = [result for result in results if result is not None]
        print(f"Successfully downloaded {len(successful_downloads)} out of {len(urls)} URLs")
        return successful_downloads

    def run_download_urls(self, urls, filenames, output_dir='filings'):
        """Download a list of URLs to a specified directory"""
        return asyncio.run(self._download_urls(urls, filenames, output_dir))

    async def _get_filing_urls_from_efts(self, base_url):
        """Asynchronously fetch all filing URLs from a given EFTS URL."""
        full_urls = []
        start, page_size = 0, 100
        async with aiohttp.ClientSession() as session:
            while True:
                tasks = [self._fetch_json_from_url(session, f"{base_url}&from={start + i * page_size}") for i in range(10)]
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
        """Get the number of filings from a given EFTS URL."""
        response = requests.get(url, headers=self.headers)
        return sum(bucket['doc_count'] for bucket in response.json()['aggregations']['form_filter']['buckets'])

    def _subset_urls(self, full_url, total_filings, target_filings_per_range=1000):
        """Split an EFTS URL into multiple URLs based on the number of filings."""
        parsed_url = urlparse(full_url)
        params = parse_qs(parsed_url.query)
        start = datetime.strptime(params.get('startdt', [None])[0], "%Y-%m-%d")
        end = datetime.strptime(params.get('enddt', [None])[0], "%Y-%m-%d")

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
                return [full_url]

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

        return urls[::-1]

    def _conductor(self, efts_url, return_urls, output_dir):
        """Conduct the download process based on the number of filings."""
        total_filings = self._number_of_efts_filings(efts_url)
        all_primary_doc_urls = []
        
        if total_filings < 10000:
            primary_doc_urls = asyncio.run(self._get_filing_urls_from_efts(efts_url))
            print(f"{efts_url}\nTotal filings: {len(primary_doc_urls)}")
            
            if return_urls:
                return primary_doc_urls
            else:
                filenames = [f"{url.split('/')[7]}_{url.split('/')[-1]}" for url in primary_doc_urls]
                self.run_download_urls(urls=primary_doc_urls, filenames=filenames, output_dir=output_dir)
                return None
        
        for subset_url in self._subset_urls(efts_url, total_filings):
            sub_primary_doc_urls = self._conductor(efts_url=subset_url, return_urls=True, output_dir=output_dir)
            
            if return_urls:
                all_primary_doc_urls.extend(sub_primary_doc_urls)
            else:
                filenames = [f"{url.split('/')[7]}_{url.split('/')[-1]}" for url in sub_primary_doc_urls]
                self.run_download_urls(urls=sub_primary_doc_urls, filenames=filenames, output_dir=output_dir)
        
        return all_primary_doc_urls if return_urls else None

    def download(self, output_dir='filings', return_urls=False, cik=None, ticker=None, form=None, date=None):
        """Download filings based on CIK, ticker, form, and date. Date can be a single date, date range, or list of dates."""
        base_url = "https://efts.sec.gov/LATEST/search-index"
        params = {}

        if sum(x is not None for x in [cik, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik or ticker')
        
        if ticker is not None:
            cik = identifier_to_cik(ticker)
                
        if cik:
            if isinstance(cik, list):
                formatted_ciks = ','.join(str(c).zfill(10) for c in cik)
            else:
                formatted_ciks = str(cik).zfill(10)
            params['ciks'] = formatted_ciks
        
        params['forms'] = ','.join(form) if isinstance(form, list) else form if form else "-0"
        
        if isinstance(date, list):
            efts_url_list = [self.generate_url(base_url, {**params, 'startdt': d, 'enddt': d}) for d in date]
        elif isinstance(date, tuple):
            efts_url_list = [self.generate_url(base_url, {**params, 'startdt': date[0], 'enddt': date[1]})]
        else:
            date_str = date if date else f"2001-01-01,{datetime.now().strftime('%Y-%m-%d')}"
            efts_url_list = [self.generate_url(base_url, {**params, 'startdt': date_str.split(',')[0], 'enddt': date_str.split(',')[1]})]
        
        all_primary_doc_urls = []
        for efts_url in efts_url_list:
            if return_urls:
                all_primary_doc_urls.extend(self._conductor(efts_url=efts_url, return_urls=True, output_dir=output_dir))
            else:
                self._conductor(efts_url=efts_url, return_urls=False, output_dir=output_dir)
        
        return all_primary_doc_urls if return_urls else None

    def download_company_concepts(self, output_dir='company_concepts', cik=None, ticker=None):
            if sum(x is not None for x in [cik, ticker]) > 1:
                raise ValueError('Please provide no more than one identifier: cik or ticker')
            
            ciks = None
            if cik:
                if isinstance(cik, list):
                    ciks = cik
                else:
                    ciks = [cik]
            
            if ticker is not None:
                ciks = identifier_to_cik(ticker)

            if ciks is None:
                company_tickers = load_company_tickers()
                ciks = [company['cik'] for company in company_tickers]
                
            os.makedirs(output_dir, exist_ok=True)
                    
            urls = [f'https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json' for cik in ciks]
            filenames = [f"CIK{str(cik).zfill(10)}.json" for cik in ciks]
            self.run_download_urls(urls=urls, filenames=filenames, output_dir=output_dir)


    def download_dataset(self, dataset, dataset_path='datasets'):
        """Download a dataset from Dropbox. Currently supports 'parsed_10k' and 'mda'."""
        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)

        if dataset == 'parsed_10k':
            file_path = os.path.join(dataset_path, '10K.zip')
            _download_from_dropbox(dataset_10k_url, file_path)
        elif dataset == "mda":
            file_path = os.path.join(dataset_path, 'MDA.zip')
            _download_from_dropbox(dataset_mda_url, file_path)
        elif dataset == "xbrl":
            file_path = os.path.join(dataset_path, 'XBRL.zip')
            _download_from_dropbox(dataset_xbrl_url, file_path)
        elif re.match(r"10k_(\d{4})$", dataset):
            year = dataset.split('_')[-1]
            record = next((record['record'] for record in dataset_10k_record_list if record['year'] == int(year)), None)
            out_path = os.path.join(dataset_path, '10K') 
            download_from_zenodo(record, out_path)

    async def _watch_efts(self, form=None, cik=None, interval=1, silent=False):
        """Watch the EFTS API for changes in the number of filings."""
        params = {
            "startdt": datetime.now().strftime("%Y-%m-%d"),
            "enddt": datetime.now().strftime("%Y-%m-%d")
        }

        if form:
            params["forms"] = ",".join(form) if isinstance(form, list) else form
        else:
            params["forms"] = "-0"

        if cik:
            if isinstance(cik, list):
                params['ciks'] = ','.join(str(c).zfill(10) for c in cik)
            else:
                params['ciks'] = str(cik).zfill(10)

        watch_url = self.generate_url("https://efts.sec.gov/LATEST/search-index", params)
        
        previous_value = None
        async with aiohttp.ClientSession() as session:
            while True:
                data = await self._fetch_json_from_url(session, watch_url)
                
                if data:
                    if not silent:
                        print(f"URL: {watch_url}")
                    
                    current_value = data['hits']['total']['value']
                    
                    if previous_value is not None and current_value != previous_value:
                        if not silent:
                            print(f"Value changed from {previous_value} to {current_value}")
                        return True
                    
                    previous_value = current_value
                    if not silent:
                        print(f"Current value: {current_value}. Checking again in {interval} seconds.")
                else:
                    print("Error occurred while fetching data.")
                
                await asyncio.sleep(interval)

    def watch(self, interval=1, silent=True, form=None, cik=None, ticker=None):
            """Watch the EFTS API for changes in the number of filings."""
            if sum(x is not None for x in [cik, ticker]) > 1:
                raise ValueError('Please provide no more than one identifier: cik or ticker')
            
            if ticker:
                cik = identifier_to_cik(ticker)

            return asyncio.run(self._watch_efts(interval=interval, silent=silent, form=form, cik=cik))

import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import os
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode
import math
import re
import aiofiles
import json
import csv
from pkg_resources import resource_filename

from ..helper import identifier_to_cik, load_package_csv, fix_filing_url

class RetryException(Exception):
    def __init__(self, url, retry_after=601):
        self.url = url
        self.retry_after = retry_after

class Downloader:
    def __init__(self):
        self.headers = headers
        self.dataset_path = 'datasets'
        self.domain_limiters = {
            'www.sec.gov': AsyncLimiter(10, 1),
            'efts.sec.gov': AsyncLimiter(10, 1),
            'data.sec.gov': AsyncLimiter(10, 1),
            'default': AsyncLimiter(10, 1)
        }
        self.metadata = None

    def set_headers(self, user_agent):
        self.headers = {'User-Agent': user_agent}

    
    async def _fetch_content_from_url(self, session, url):
        limiter = self.get_limiter(url)
        url = fix_filing_url(url)
        async with limiter:
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 429:
                        raise RetryException(url)
                    
                    response.raise_for_status()
                    return await response.read()
            
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    raise RetryException(url)
                raise
            
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")
                raise

    async def write_content_to_file(self, content, filepath):
        """Write content to a file asynchronously."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(content)

    def generate_url(self, base_url, params):
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
        os.makedirs(output_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            total_files = len(urls)
            completed_files = 0
            
            with tqdm(total=total_files, desc="Downloading files") as pbar:
                while urls and completed_files < total_files:
                    tasks = [asyncio.create_task(self.download_file(session, url, os.path.join(output_dir, filename))) 
                             for url, filename in zip(urls, filenames) if filename]
                    
                    rate_limited = False
                    retry_after = 0
                    
                    pending = tasks
                    while pending:
                        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                        
                        for task in done:
                            try:
                                result = await task
                                completed_files += 1
                                pbar.update(1)
                            except RetryException as e:
                                print(f"\nRate limited for {e.url}. Will retry after {e.retry_after} seconds.")
                                rate_limited = True
                                retry_after = max(retry_after, e.retry_after)
                                break
                            except Exception as e:
                                print(f"\nFailed to download: {str(e)}")
                                completed_files += 1
                                pbar.update(1)
                        
                        if rate_limited:
                            break
                    
                    if rate_limited:
                        for task in pending:
                            task.cancel()
                        
                        print(f"\nRate limit hit. Sleeping for {retry_after} seconds before retrying.")
                        await asyncio.sleep(retry_after)
                        
                        # Recreate the list of URLs and filenames that haven't been processed
                        urls = [task.get_coro().cr_frame.f_locals['url'] for task in pending]
                        filenames = [filename for url, filename in zip(urls, filenames) if url in urls]
                    else:
                        break  # All tasks completed successfully

            print(f"\nSuccessfully downloaded {completed_files} out of {total_files} URLs")
            return completed_files

    def run_download_urls(self, urls, filenames, output_dir='filings'):
        """Download a list of URLs to a specified directory"""
        return asyncio.run(self._download_urls(urls, filenames, output_dir))


    async def _number_of_efts_filings(self, session, url):
        """Get the number of filings from a given EFTS URL asynchronously."""
        limiter = self.get_limiter(url)
        async with limiter:
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 429:
                        raise RetryException(url)
                    response.raise_for_status()
                    data = await response.json()
                    return sum(bucket['doc_count'] for bucket in data['aggregations']['form_filter']['buckets'])
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    raise RetryException(url)
                raise
            except Exception as e:
                print(f"Error fetching number of filings from {url}: {str(e)}")
                raise

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
    
    async def _get_filing_urls_from_efts(self, base_url, sics=None, items=None, file_types=None, save_metadata=False, output_dir=None):
        """Asynchronously fetch all filing URLs from a given EFTS URL."""
        urls = []
        start, page_size = 0, 100
        
        if save_metadata:
            metadata_file = os.path.join(output_dir, 'metadata.jsonl')
            os.makedirs(output_dir, exist_ok=True)
            
        async with aiohttp.ClientSession() as session:
            while True:
                tasks = [self._fetch_json_from_url(session, f"{base_url}&from={start + i * page_size}") for i in range(10)]
                results = await atqdm.gather(*tasks, desc="Fetching URLs")
                for data in results:
                    if data and 'hits' in data:
                        hits = data['hits']['hits']
                        if not hits:
                            return urls
                        
                        for hit in hits:
                            # Check SIC filter
                            sic_match = sics is None or any(int(sic) in sics for sic in hit['_source'].get('sics', []))
                            
                            # Check item filter
                            item_match = items is None or any(item in items for item in hit['_source'].get('items', []))
                            
                            # Check file type filter
                            file_type_match = file_types is None or hit['_source'].get('file_type') in (file_types if isinstance(file_types, list) else [file_types])
                            
                            if sic_match and item_match and file_type_match:
                                url = f"https://www.sec.gov/Archives/edgar/data/{hit['_source']['ciks'][0]}/{hit['_id'].split(':')[0].replace('-', '')}/{hit['_id'].split(':')[1]}"
                                urls.append(url)
                                
                                if save_metadata:
                                    accession_num = hit['_id'].split(':')[0].replace('-', '')
                                    metadata = {accession_num: hit}
                                    async with aiofiles.open(metadata_file, 'a') as f:
                                        await f.write(json.dumps(metadata) + '\n')
                        
                        if start + page_size > data['hits']['total']['value']:
                            return urls
                start += 10 * page_size
        return urls
    
    async def _conductor(self, efts_url, output_dir, sics, items, file_types, save_metadata=False):
        """Conduct the download process based on the number of filings."""
        async with aiohttp.ClientSession() as session:
            try:
                total_filings = await self._number_of_efts_filings(session, efts_url)
            except RetryException as e:
                print(f"Rate limited when fetching number of filings. Retrying after {e.retry_after} seconds.")
                await asyncio.sleep(e.retry_after)
                return await self._conductor(efts_url, output_dir, sics, items, file_types, save_metadata)

        if total_filings < 10000:
            urls = await self._get_filing_urls_from_efts(efts_url, sics=sics, items=items, file_types=file_types, save_metadata=save_metadata, output_dir=output_dir)
            print(f"{efts_url}\nTotal filings: {len(urls)}")
            filenames = [f"{url.split('/')[7]}_{url.split('/')[-1]}" for url in urls]
            await self._download_urls(urls=urls, filenames=filenames, output_dir=output_dir)
        else:
            for subset_url in self._subset_urls(efts_url, total_filings):
                await self._conductor(efts_url=subset_url, output_dir=output_dir, sics=sics, items=items, file_types=file_types, save_metadata=save_metadata)


    def download(self, output_dir='filings', cik=None, ticker=None, form=None, 
                date=None, sics=None, items=None, file_types=None, save_metadata=False):
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
        
        if file_types:
            params['q'] = '-'
            if isinstance(file_types, list):
                params['file_type'] = ','.join(file_types)
            else:
                params['file_type'] = file_types
        
        if isinstance(date, list):
            efts_url_list = [self.generate_url(base_url, {**params, 'startdt': d, 'enddt': d}) for d in date]
        elif isinstance(date, tuple):
            efts_url_list = [self.generate_url(base_url, {**params, 'startdt': date[0], 'enddt': date[1]})]
        else:
            date_str = date if date else f"2001-01-01,{datetime.now().strftime('%Y-%m-%d')}"
            efts_url_list = [self.generate_url(base_url, {**params, 'startdt': date_str.split(',')[0], 'enddt': date_str.split(',')[1]})]
        
        for efts_url in efts_url_list:
            asyncio.run(self._conductor(efts_url=efts_url, output_dir=output_dir, sics=sics, items=items, file_types=file_types, save_metadata=save_metadata))

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
            company_tickers = load_package_csv('company_tickers')
            ciks = [company['cik'] for company in company_tickers]
            
        os.makedirs(output_dir, exist_ok=True)
                
        urls = [f'https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json' for cik in ciks]
        filenames = [f"CIK{str(cik).zfill(10)}.json" for cik in ciks]
        self.run_download_urls(urls=urls, filenames=filenames, output_dir=output_dir)
    

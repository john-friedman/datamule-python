import asyncio
import aiohttp
import os
from tqdm import tqdm
from datetime import datetime
from urllib.parse import urlencode
import aiofiles
import json
import time
from collections import deque

from ..helper import identifier_to_cik, load_package_csv, fix_filing_url, headers
from ..parser.sgml_parsing.sgml_parser_cy import parse_sgml_submission

class RetryException(Exception):
    def __init__(self, url, retry_after=601):
        self.url = url
        self.retry_after = retry_after

class PreciseRateLimiter:
    def __init__(self, rate, interval=1.0):
        self.rate = rate  # requests per interval
        self.interval = interval  # in seconds
        self.token_time = self.interval / self.rate  # time per token
        self.last_time = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            wait_time = self.last_time + self.token_time - now
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self.last_time = time.time()
            return True

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

class RateMonitor:
    def __init__(self, window_size=1.0):
        self.window_size = window_size
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def add_request(self, size_bytes):
        async with self._lock:
            now = time.time()
            self.requests.append((now, size_bytes))
            while self.requests and self.requests[0][0] < now - self.window_size:
                self.requests.popleft()
    
    def get_current_rates(self):
        now = time.time()
        while self.requests and self.requests[0][0] < now - self.window_size:
            self.requests.popleft()
        
        if not self.requests:
            return 0, 0
        
        request_count = len(self.requests)
        byte_count = sum(size for _, size in self.requests)
        
        requests_per_second = request_count / self.window_size
        mb_per_second = (byte_count / 1024 / 1024) / self.window_size
        
        return round(requests_per_second, 1), round(mb_per_second, 2)

class Downloader:
    def __init__(self):
        self.headers = headers
        self.limiter = PreciseRateLimiter(5)  # 10 requests per second
        self.session = None
        self.parse_filings = True
        self.download_queue = asyncio.Queue()
        self.rate_monitor = RateMonitor()
        self.current_pbar = None
        self.connection_semaphore = asyncio.Semaphore(5)
    
    def update_progress_description(self):
        if self.current_pbar:
            reqs_per_sec, mb_per_sec = self.rate_monitor.get_current_rates()
            self.current_pbar.set_description(
                f"Progress [Rate: {reqs_per_sec}/s | {mb_per_sec} MB/s]"
            )

    async def __aenter__(self):
        await self._init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close()

    async def _init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def _close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def _fetch_json(self, url):
        """Fetch JSON with rate monitoring."""
        async with self.limiter:
            try:
                url = fix_filing_url(url)
                async with self.session.get(url) as response:
                    if response.status == 429:
                        raise RetryException(url)
                    response.raise_for_status()
                    content = await response.read()
                    await self.rate_monitor.add_request(len(content))
                    self.update_progress_description()
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    raise RetryException(url)
                raise

    async def _get_filing_urls_from_efts(self, base_url):
        """Fetch filing URLs from EFTS in batches."""
        start = 0
        page_size = 100
        urls = []
        
        data = await self._fetch_json(f"{base_url}&from=0&size=1")
        if not data or 'hits' not in data:
            return []
            
        total_hits = data['hits']['total']['value']
        if not total_hits:
            return []

        pbar = tqdm(total=total_hits, desc="Fetching URLs [Rate: 0/s | 0 MB/s]")
        self.current_pbar = pbar
        
        while start < total_hits:
            try:
                tasks = [
                    self._fetch_json(f"{base_url}&from={start + i * page_size}&size={page_size}") 
                    for i in range(10)
                ]
                
                results = await asyncio.gather(*tasks)
                
                for data in results:
                    if data and 'hits' in data:
                        hits = data['hits']['hits']
                        if hits:
                            batch_urls = [
                                f"https://www.sec.gov/Archives/edgar/data/{hit['_source']['ciks'][0]}/{hit['_id'].split(':')[0]}.txt" 
                                for hit in hits
                            ]
                            urls.extend(batch_urls)
                            pbar.update(len(hits))
                            self.update_progress_description()
                
                start += 10 * page_size

            except RetryException as e:
                print(f"\nRate limited. Sleeping for {e.retry_after} seconds...")
                await asyncio.sleep(e.retry_after)
                continue
            except Exception as e:
                print(f"\nError fetching URLs batch at {start}: {str(e)}")
                break

        pbar.close()
        self.current_pbar = None
        return urls

    async def _download_file(self, url, filepath):
        """Download single file with precise rate limiting."""
        async with self.connection_semaphore:
            async with self.limiter:
                try:
                    url = fix_filing_url(url)
                    async with self.session.get(url) as response:
                        if response.status == 429:
                            raise RetryException(url)
                        response.raise_for_status()
                        content = await response.read()
                        await self.rate_monitor.add_request(len(content))
                        self.update_progress_description()
                        
                        parsed_data = None
                        if self.parse_filings:
                            try:
                                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                                async with aiofiles.open(filepath, 'wb') as f:
                                    await f.write(content)

                                parsed_data = parse_sgml_submission(
                                    content=content.decode(), 
                                    output_dir=os.path.dirname(filepath) + f'/{url.split("/")[-1].split(".")[0].replace("-", "")}'
                                )
                                
                                try:
                                    os.remove(filepath)
                                except Exception as e:
                                    print(f"\nError deleting original file {filepath}: {str(e)}")
                                    
                            except Exception as e:
                                print(f"\nError parsing {url}: {str(e)}")
                                try:
                                    os.remove(filepath)
                                    parsed_dir = os.path.dirname(filepath) + f'/{url.split("/")[-1].split(".")[0].replace("-", "")}'
                                    if os.path.exists(parsed_dir):
                                        import shutil
                                        shutil.rmtree(parsed_dir)
                                except Exception as e:
                                    print(f"\nError cleaning up files for {url}: {str(e)}")
                        else:
                            os.makedirs(os.path.dirname(filepath), exist_ok=True)
                            async with aiofiles.open(filepath, 'wb') as f:
                                await f.write(content)
                        
                        return filepath, parsed_data

                except Exception as e:
                    print(f"\nError downloading {url}: {str(e)}")
                    return None

    async def _download_worker(self, pbar):
        """Worker to process download queue."""
        while True:
            try:
                url, filepath = await self.download_queue.get()
                result = await self._download_file(url, filepath)
                if result:
                    pbar.update(1)
                self.download_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"\nWorker error processing {url}: {str(e)}")
                self.download_queue.task_done()

    async def _download_and_process(self, urls, output_dir):
        """Queue-based download processing."""
        results = []
        parsed_results = []
        
        pbar = tqdm(total=len(urls), desc="Downloading files [Rate: 0/s | 0 MB/s]")
        self.current_pbar = pbar
        
        for url in urls:
            filename = url.split('/')[-1]
            filepath = os.path.join(output_dir, filename)
            await self.download_queue.put((url, filepath))
        
        workers = [asyncio.create_task(self._download_worker(pbar)) 
                  for _ in range(5)]  # Match number of workers to semaphore
        
        await self.download_queue.join()
        
        for worker in workers:
            worker.cancel()
        
        await asyncio.gather(*workers, return_exceptions=True)
        
        pbar.close()
        self.current_pbar = None
        return results, parsed_results

    def download_submissions(self, output_dir='filings', cik=None, ticker=None, submission_type=None, date=None, parse=True):
        """Main method to download SEC filings."""
        self.parse_filings = parse
        
        async def _download():
            async with self as downloader:
                if ticker is not None:
                    cik_value = identifier_to_cik(ticker)
                else:
                    cik_value = cik

                params = {}
                if cik_value:
                    if isinstance(cik_value, list):
                        params['ciks'] = ','.join(str(c).zfill(10) for c in cik_value)
                    else:
                        params['ciks'] = str(cik_value).zfill(10)

                params['forms'] = ','.join(submission_type) if isinstance(submission_type, list) else submission_type if submission_type else "-0"

                if isinstance(date, list):
                    dates = [(d, d) for d in date]
                elif isinstance(date, tuple):
                    dates = [date]
                else:
                    date_str = date if date else f"2001-01-01,{datetime.now().strftime('%Y-%m-%d')}"
                    start, end = date_str.split(',')
                    dates = [(start, end)]

                all_filepaths = []
                all_parsed_data = []
                
                for start_date, end_date in dates:
                    params['startdt'] = start_date
                    params['enddt'] = end_date
                    base_url = "https://efts.sec.gov/LATEST/search-index"
                    efts_url = f"{base_url}?{urlencode(params, doseq=True)}"
                    
                    urls = await self._get_filing_urls_from_efts(efts_url)
                    if urls:
                        filepaths, parsed_data = await self._download_and_process(urls, output_dir)
                        all_filepaths.extend(filepaths)
                        all_parsed_data.extend(parsed_data)

                return all_filepaths, all_parsed_data

        return asyncio.run(_download())

    def download_company_concepts(self, output_dir='company_concepts', cik=None, ticker=None):
        """Download company concept data."""
        async def _download_concepts():
            async with self as downloader:
                if ticker is not None:
                    ciks = identifier_to_cik(ticker)
                elif cik:
                    ciks = [cik] if not isinstance(cik, list) else cik
                else:
                    company_tickers = load_package_csv('company_tickers')
                    ciks = [company['cik'] for company in company_tickers]

                os.makedirs(output_dir, exist_ok=True)
                urls = [f'https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json' for cik in ciks]
                
                pbar = tqdm(total=len(urls), desc="Downloading concepts [Rate: 0/s | 0 MB/s]")
                self.current_pbar = pbar
                
                for url in urls:
                    filename = url.split('/')[-1]
                    filepath = os.path.join(output_dir, filename)
                    await self.download_queue.put((url, filepath))
                
                workers = [asyncio.create_task(self._download_worker(pbar)) 
                          for _ in range(5)]
                
                await self.download_queue.join()
                
                for worker in workers:
                    worker.cancel()
                
                await asyncio.gather(*workers, return_exceptions=True)
                
                pbar.close()
                self.current_pbar = None
                
                results = []
                for url in urls:
                    filename = url.split('/')[-1]
                    filepath = os.path.join(output_dir, filename)
                    if os.path.exists(filepath):
                        results.append(filepath)
                
                return results

        return asyncio.run(_download_concepts())
import asyncio
import aiohttp
from tqdm import tqdm
from datetime import datetime
from urllib.parse import urlencode
import time

class PreciseRateLimiter:
    def __init__(self, rate=10, interval=1.0):
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

class EFTSQuery:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Your Name yourname@email.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'efts.sec.gov'
        }
        self.session = None
        self.limiter = PreciseRateLimiter(10)

    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None

    async def _fetch_json(self, url):
        await self.limiter.acquire()
        try:
            async with self.session.get(url) as response:
                if response.status == 429:
                    await asyncio.sleep(61)
                    return await self._fetch_json(url)
                return await response.json()
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    async def _get_accession_numbers(self, base_url):
        data = await self._fetch_json(f"{base_url}&from=0&size=1")
        if not data or 'hits' not in data:
            return []
            
        total_hits = data['hits']['total']['value']
        if not total_hits:
            return []

        accession_numbers = []
        start = 0
        page_size = 100
        batch_size = 10  # Number of concurrent requests
        
        with tqdm(total=total_hits) as pbar:
            while start < total_hits:
                tasks = []
                for i in range(batch_size):
                    if start + i * page_size >= total_hits:
                        break
                    url = f"{base_url}&from={start + i * page_size}&size={page_size}"
                    tasks.append(self._fetch_json(url))
                
                if not tasks:
                    break
                    
                results = await asyncio.gather(*tasks)
                
                for data in results:
                    if data and 'hits' in data:
                        hits = data['hits']['hits']
                        batch_numbers = [
                            f"{hit['_source']['ciks'][0]}/{hit['_id'].split(':')[0]}"
                            for hit in hits
                        ]
                        accession_numbers.extend(batch_numbers)
                        pbar.update(len(hits))
                
                start += batch_size * page_size

        return accession_numbers

    def query_efts(self, cik=None, ticker=None, submission_type=None, filing_date=None, search_text=None):
        async def _download():
            async with self as downloader:
                params = {}
                
                if cik:
                    params['ciks'] = str(cik).zfill(10)

                if submission_type:
                    params['forms'] = ','.join(submission_type) if isinstance(submission_type, list) else submission_type

                if isinstance(filing_date, list):
                    dates = [(d, d) for d in filing_date]
                elif isinstance(filing_date, tuple):
                    dates = [filing_date]
                else:
                    date_str = filing_date if filing_date else f"2001-01-01,{datetime.now().strftime('%Y-%m-%d')}"
                    start, end = date_str.split(',')
                    dates = [(start, end)]
                
                params['startdt'], params['enddt'] = dates[0]

                if search_text:
                    params['q'] = f'"{search_text}"'

                base_url = f"https://efts.sec.gov/LATEST/search-index?{urlencode(params, doseq=True)}"
                return await self._get_accession_numbers(base_url)

        return asyncio.run(_download())
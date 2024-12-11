import asyncio
import aiohttp
import time
import os
import json
from datetime import datetime
from urllib.parse import urlencode
from tqdm import tqdm
from aiolimiter import AsyncLimiter

from ..helper import identifier_to_cik, load_package_csv, fix_filing_url, headers
from ..parser.sgml_parsing.sgml_parser_cy import parse_sgml_submission

class Downloader:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(5)
        self.limiter = AsyncLimiter(10, 1)
        self.session = None
        self.headers = headers

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

    async def _fetch(self, url):
        if not self.session:
            raise RuntimeError("Session not initialized. Use async with Downloader() as downloader:")
        
        async with self.semaphore:
            async with self.limiter:
                url = fix_filing_url(url)
                async with self.session.get(url) as response:
                    if response.status != 200:
                        raise aiohttp.ClientError(f"HTTP {response.status}: {response.reason}")
                    return await response.text()

    async def _fetch_json(self, url):
        content = await self._fetch(url)
        return json.loads(content)

    async def _get_filing_urls_from_efts(self, base_url):
        """Fetch all filing URLs from EFTS asynchronously."""
        urls = []
        start, page_size = 0, 100

        while True:
            try:
                data = await self._fetch_json(f"{base_url}&from={start}")
                if not data or 'hits' not in data:
                    break

                hits = data['hits']['hits']
                if not hits:
                    break

                for hit in hits:
                    url = f"https://www.sec.gov/Archives/edgar/data/{hit['_source']['ciks'][0]}/{hit['_id'].split(':')[0]}.txt"
                    urls.append(url)

                if start + page_size > data['hits']['total']['value']:
                    break
                    
                start += page_size

            except Exception as e:
                print(f"Error fetching URLs: {str(e)}")
                break

        return urls

    async def _download_and_parse(self, urls, output_dir):
        """Download and parse multiple filings with progress tracking."""
        async def process_single(url):
            try:
                content = await self._fetch(url)
                submission_dir = output_dir + "/" + url.split('/')[-1].split('.')[0].replace('-', '')
                return parse_sgml_submission(content=content, output_dir=submission_dir)
            except Exception as e:
                print(f"\nError processing {url}: {str(e)}")
                return None

        tasks = [process_single(url) for url in urls]
        results = []
        
        for task in tqdm(asyncio.as_completed(tasks), total=len(urls), desc="Processing filings"):
            result = await task
            if result is not None:
                results.append(result)
        
        return results

    def download(self, output_dir='filings', cik=None, ticker=None, form=None, date=None):
        """Main method to download and parse SEC filings."""
        async def _download():
            async with self as downloader:
                # Handle identifiers
                if ticker is not None:
                    cik_value = identifier_to_cik(ticker)
                else:
                    cik_value = cik

                # Prepare parameters
                params = {}
                if cik_value:
                    if isinstance(cik_value, list):
                        params['ciks'] = ','.join(str(c).zfill(10) for c in cik_value)
                    else:
                        params['ciks'] = str(cik_value).zfill(10)

                params['forms'] = ','.join(form) if isinstance(form, list) else form if form else "-0"

                # Handle dates
                if isinstance(date, list):
                    dates = [(d, d) for d in date]
                elif isinstance(date, tuple):
                    dates = [date]
                else:
                    date_str = date if date else f"2001-01-01,{datetime.now().strftime('%Y-%m-%d')}"
                    start, end = date_str.split(',')
                    dates = [(start, end)]

                all_results = []
                for start_date, end_date in dates:
                    params['startdt'] = start_date
                    params['enddt'] = end_date
                    base_url = "https://efts.sec.gov/LATEST/search-index"
                    efts_url = f"{base_url}?{urlencode(params, doseq=True)}"
                    
                    urls = await self._get_filing_urls_from_efts(efts_url)
                    
                    if urls:
                        results = await self._download_and_parse(urls, output_dir)
                        all_results.extend(results)

                return all_results

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

                urls = [f'https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json' for cik in ciks]
                results = []
                
                for url in tqdm(urls, desc="Downloading company concepts"):
                    try:
                        content = await downloader._fetch(url)
                        if output_dir:
                            os.makedirs(output_dir, exist_ok=True)
                            filename = url.split('/')[-1]
                            with open(os.path.join(output_dir, filename), 'w') as f:
                                f.write(content)
                        results.append(json.loads(content))
                    except Exception as e:
                        print(f"\nError downloading {url}: {str(e)}")

                return results

        return asyncio.run(_download_concepts())
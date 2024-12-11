import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import os
from tqdm import tqdm
from datetime import datetime
from urllib.parse import urlencode
import aiofiles
import json

from ..helper import identifier_to_cik, load_package_csv, fix_filing_url, headers
from ..parser.sgml_parsing.sgml_parser_cy import parse_sgml_submission

class RetryException(Exception):
    def __init__(self, url, retry_after=601):
        self.url = url
        self.retry_after = retry_after

class Downloader:
    def __init__(self):
        self.headers = headers
        self.limiter = AsyncLimiter(10, 1)  # 10 requests per second
        self.session = None
        self.parse_filings = True  # Flag to control parsing

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
        """Fetch JSON with rate limiting and retries."""
        async with self.limiter:
            try:
                url = fix_filing_url(url)
                async with self.session.get(url) as response:
                    if response.status == 429:
                        raise RetryException(url)
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    raise RetryException(url)
                raise

    async def _get_filing_urls_from_efts(self, base_url):
        """Fetch filing URLs from EFTS in batches with progress tracking."""
        start = 0
        page_size = 100
        urls = []
        
        # Get total number first
        data = await self._fetch_json(f"{base_url}&from=0&size=1")
        if not data or 'hits' not in data:
            return []
            
        total_hits = data['hits']['total']['value']
        if not total_hits:
            return []

        # Create progress bar
        pbar = tqdm(total=total_hits, desc="Fetching filing URLs")
        
        while start < total_hits:
            try:
                # Create 10 tasks at once
                tasks = [
                    self._fetch_json(f"{base_url}&from={start + i * page_size}&size={page_size}") 
                    for i in range(10)
                ]
                
                # Run all 10 tasks concurrently
                results = await asyncio.gather(*tasks)
                
                # Process results
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
                
                # Move forward by 1000 (10 tasks × 100 per page)
                start += 10 * page_size

            except RetryException as e:
                print(f"\nRate limited. Sleeping for {e.retry_after} seconds...")
                await asyncio.sleep(e.retry_after)
                continue
            except Exception as e:
                print(f"\nError fetching URLs batch at {start}: {str(e)}")
                break

        pbar.close()
        return urls
    
    async def _download_file(self, url, filepath):
        """Download single file with rate limiting and parse SGML content."""
        async with self.limiter:
            try:
                url = fix_filing_url(url)
                async with self.session.get(url) as response:
                    if response.status == 429:
                        raise RetryException(url)
                    response.raise_for_status()
                    content = await response.read()
                    
                    # Parse SGML content in memory if enabled
                    parsed_data = None
                    if self.parse_filings:
                        try:
                            # Save content temporarily
                            os.makedirs(os.path.dirname(filepath), exist_ok=True)
                            async with aiofiles.open(filepath, 'wb') as f:
                                await f.write(content)

                            # Try to parse
                            parsed_data = parse_sgml_submission(
                                content=content.decode(), 
                                output_dir=os.path.dirname(filepath) + f'/{url.split("/")[-1].split(".")[0].replace("-", "")}'
                            )
                            
                            # If we get here, parsing was successful, delete original file
                            try:
                                os.remove(filepath)
                            except Exception as e:
                                print(f"\nError deleting original file {filepath}: {str(e)}")
                                
                        except Exception as e:
                            print(f"\nError parsing {url}: {str(e)}")
                            # Parsing failed, delete both original and any partial parsed files
                            try:
                                os.remove(filepath)  # Delete original
                                parsed_dir = os.path.dirname(filepath) + f'/{url.split("/")[-1].split(".")[0].replace("-", "")}'
                                if os.path.exists(parsed_dir):
                                    import shutil
                                    shutil.rmtree(parsed_dir)  # Delete any partial parsed files
                            except Exception as e:
                                print(f"\nError cleaning up files for {url}: {str(e)}")
                    else:
                        # Parsing disabled, just save the file
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        async with aiofiles.open(filepath, 'wb') as f:
                            await f.write(content)
                    
                    return filepath, parsed_data

            except Exception as e:
                print(f"\nError downloading {url}: {str(e)}")
                return None
    

    async def _download_and_process(self, urls, output_dir):
        """Download files with progress tracking. Max 5 concurrent downloads."""
        results = []
        parsed_results = []
        semaphore = asyncio.Semaphore(5)  # Limit concurrent downloads to 5
        
        async def download_with_sem(url, filepath):
            async with semaphore:
                return await self._download_file(url, filepath)
        
        with tqdm(total=len(urls), desc="Downloading filings") as pbar:
            for i in range(0, len(urls), 5):
                chunk = urls[i:i+5]
                tasks = []
                
                # Create tasks for this chunk
                for url in chunk:
                    filename = url.split('/')[-1]
                    filepath = os.path.join(output_dir, filename)
                    tasks.append(asyncio.create_task(download_with_sem(url, filepath)))
                
                # Process chunk with rate limiting
                try:
                    chunk_results = await asyncio.gather(*tasks)
                    for result in chunk_results:
                        if result:
                            filepath, parsed_data = result
                            results.append(filepath)
                            if parsed_data:
                                parsed_results.append(parsed_data)
                            pbar.update(1)
                except RetryException as e:
                    print(f"\nRate limited. Sleeping for {e.retry_after} seconds...")
                    await asyncio.sleep(e.retry_after)
                    # Failed URLs will need to be retried
                    failed_urls = chunk[len(results) - i:]
                    urls.extend(failed_urls)
                except Exception as e:
                    print(f"\nError in chunk: {str(e)}")
                    pbar.update(len(chunk))

        return results, parsed_results

    def download_filings(self, output_dir='filings', cik=None, ticker=None, form=None, date=None, parse=True):
        """Main method to download SEC filings."""
        self.parse_filings = parse
        
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

                all_filepaths = []
                all_parsed_data = []
                
                for start_date, end_date in dates:
                    params['startdt'] = start_date
                    params['enddt'] = end_date
                    base_url = "https://efts.sec.gov/LATEST/search-index"
                    efts_url = f"{base_url}?{urlencode(params, doseq=True)}"
                    
                    # Get URLs and download in batches
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
                
                results = []
                semaphore = asyncio.Semaphore(5)
                
                async def download_with_sem(url):
                    async with semaphore:
                        filename = url.split('/')[-1]
                        filepath = os.path.join(output_dir, filename)
                        result, _ = await self._download_file(url, filepath)
                        return result
                
                with tqdm(total=len(urls), desc="Downloading company concepts") as pbar:
                    for i in range(0, len(urls), 5):
                        chunk = urls[i:i+5]
                        tasks = [asyncio.create_task(download_with_sem(url)) for url in chunk]
                        
                        try:
                            chunk_results = await asyncio.gather(*tasks)
                            for result in chunk_results:
                                if result:
                                    results.append(result)
                                    pbar.update(1)
                        except RetryException as e:
                            print(f"\nRate limited. Sleeping for {e.retry_after} seconds...")
                            await asyncio.sleep(e.retry_after)
                            failed_urls = chunk[len(results) - i:]
                            urls.extend(failed_urls)
                        except Exception as e:
                            print(f"\nError in chunk: {str(e)}")
                            pbar.update(len(chunk))

                return results

        return asyncio.run(_download_concepts())
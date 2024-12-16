import os
import asyncio
import aiohttp
from pathlib import Path
from tqdm import tqdm
import time
import shutil
import ssl
import zstandard as zstd
import io
import json
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from queue import Queue, Empty
from threading import Thread
from datamule.parser.sgml_parsing.sgml_parser_cy import parse_sgml_submission
import urllib.parse
from ..helper import identifier_to_cik

class InsufficientBalanceError(Exception):
    def __init__(self, required_cost, current_balance, total_urls):
        self.required_cost = required_cost
        self.current_balance = current_balance
        self.total_urls = total_urls
        message = (f"Insufficient balance. Required: ${required_cost:.4f}, "
                  f"Current balance: ${current_balance:.4f}, "
                  f"Total URLs: {total_urls}")
        super().__init__(message)

class PremiumDownloader:
    def __init__(self, api_key=None):
        self.BASE_URL = "https://library.datamule.xyz/original/nc/"
        self.API_BASE_URL = "https://sec-library.jgfriedman99.workers.dev/"
        self.CHUNK_SIZE = 2 * 1024 * 1024
        self.MAX_CONCURRENT_DOWNLOADS = 100
        self.MAX_DECOMPRESSION_WORKERS = 16
        self.MAX_PROCESSING_WORKERS = 16
        self.QUEUE_SIZE = 10
        if api_key is not None:
            self._api_key = api_key

    @property
    def api_key(self):
        return getattr(self, '_api_key', None) or os.getenv('DATAMULE_API_KEY')

    @api_key.setter
    def api_key(self, value):
        if not value:
            raise ValueError("API key cannot be empty")
        self._api_key = value

    def _log_error(self, output_dir, filename, error_msg):
        error_file = os.path.join(output_dir, 'errors.json')
        try:
            if os.path.exists(error_file):
                with open(error_file, 'r') as f:
                    errors = json.load(f)
            else:
                errors = {}
            
            errors[filename] = str(error_msg)
            
            with open(error_file, 'w') as f:
                json.dump(errors, f, indent=2)
        except Exception as e:
            print(f"Failed to log error to {error_file}: {str(e)}")

    async def _fetch_submissions(self, session, submission_type=None, cik=None, filing_date=None, page=1):
        params = {
            'api_key': self.api_key,
            'page': page
        }
        
        if submission_type:
            if isinstance(submission_type, list):
                params['submission_type'] = ','.join(str(x) for x in submission_type)
            else:
                params['submission_type'] = str(submission_type)
        
        if cik:
            if isinstance(cik, list):
                params['cik'] = ','.join(str(x) for x in cik)
            else:
                params['cik'] = str(cik)
        
        if filing_date:
            if isinstance(filing_date, tuple):
                params['startdt'] = str(filing_date[0])
                params['enddt'] = str(filing_date[1])
            else:
                if isinstance(filing_date, list):
                    params['filing_date'] = ','.join(str(x) for x in filing_date)
                else:
                    params['filing_date'] = str(filing_date)

        url = f"{self.API_BASE_URL}?{urllib.parse.urlencode(params)}"
        
        async with session.get(url) as response:
            data = await response.json()
            if not data.get('success'):
                raise ValueError(f"API request failed: {data.get('error')}")

            charges = data['metadata']['billing']['charges']
            print(f"\nCost: ${charges['results']:.12f} downloads + ${charges['rows_read']:.12f} row reads = ${charges['total']:.12f}")
            print(f"Balance: ${data['metadata']['billing']['remaining_balance']:.12f}")
            
            urls = [f"{self.BASE_URL}{str(sub['accession_number']).zfill(18)}.sgml{'.zst' if sub.get('compressed', '').lower() == 'true' else ''}" for sub in data['data']]
            return urls, data['metadata']['pagination']

    class FileProcessor:
        def __init__(self, output_dir, max_workers, queue_size, pbar, downloader):
            self.processing_queue = Queue(maxsize=queue_size)
            self.should_stop = False
            self.processing_workers = []
            self.output_dir = output_dir
            self.max_workers = max_workers
            self.batch_size = 10
            self.pbar = pbar
            self.downloader = downloader

        def start_processing_workers(self):
            for _ in range(self.max_workers):
                worker = Thread(target=self._processing_worker)
                worker.daemon = True
                worker.start()
                self.processing_workers.append(worker)

        def _process_file(self, item):
            filename, content = item
            clean_name = filename[:-4] if filename.endswith('.zst') else filename
            output_path = os.path.join(self.output_dir, Path(clean_name).stem)
            try:
                parse_sgml_submission(None, output_dir=output_path, content=content)
                self.pbar.update(1)
            except Exception as e:
                self.downloader._log_error(self.output_dir, filename, str(e))

        def _processing_worker(self):
            batch = []
            while not self.should_stop:
                try:
                    item = self.processing_queue.get(timeout=1)
                    if item is None:
                        break

                    batch.append(item)

                    if len(batch) >= self.batch_size or self.processing_queue.empty():
                        for item in batch:
                            self._process_file(item)
                            self.processing_queue.task_done()
                        batch = []

                except Empty:
                    if batch:
                        for item in batch:
                            self._process_file(item)
                            self.processing_queue.task_done()
                        batch = []

        def stop_workers(self):
            self.should_stop = True
            for _ in self.processing_workers:
                self.processing_queue.put(None)
            for worker in self.processing_workers:
                worker.join()

    def decompress_stream(self, compressed_chunks, filename, output_dir, processor):
        dctx = zstd.ZstdDecompressor()
        try:
            input_buffer = io.BytesIO(b''.join(compressed_chunks))
            decompressed_content = io.BytesIO()
            
            with dctx.stream_reader(input_buffer) as reader:
                shutil.copyfileobj(reader, decompressed_content)
                
            content = decompressed_content.getvalue().decode('utf-8')
            processor.processing_queue.put((filename, content))
            return True
                
        except Exception as e:
            self._log_error(output_dir, filename, f"Decompression error: {str(e)}")
            return False
        finally:
            try:
                input_buffer.close()
                decompressed_content.close()
            except:
                pass

    def save_regular_file(self, chunks, filename, output_dir, processor):
        try:
            content = b''.join(chunks).decode('utf-8')
            processor.processing_queue.put((filename, content))
            return True
                
        except Exception as e:
            self._log_error(output_dir, filename, f"Error saving file: {str(e)}")
            return False

    async def download_and_process(self, session, url, semaphore, decompression_pool, output_dir, processor):
        async with semaphore:
            chunks = []
            filename = url.split('/')[-1]

            api_key = self.api_key
            if not api_key:
                raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")

            try:
                headers = {
                    'Connection': 'keep-alive',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Authorization': f'Bearer {api_key}'
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        async for chunk in response.content.iter_chunked(self.CHUNK_SIZE):
                            chunks.append(chunk)

                        loop = asyncio.get_running_loop()
                        if filename.endswith('.zst'):
                            success = await loop.run_in_executor(
                                decompression_pool,
                                partial(self.decompress_stream, chunks, filename, output_dir, processor)
                            )
                        else:
                            success = await loop.run_in_executor(
                                decompression_pool,
                                partial(self.save_regular_file, chunks, filename, output_dir, processor)
                            )

                        if not success:
                            self._log_error(output_dir, filename, "Failed to process file")
                    elif response.status == 401:
                        self._log_error(output_dir, filename, "Authentication failed: Invalid API key")
                        raise ValueError("Invalid API key")
                    else:
                        self._log_error(output_dir, filename, f"Download failed: Status {response.status}")
            except Exception as e:
                self._log_error(output_dir, filename, str(e))

    async def process_batch(self, urls, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
        with tqdm(total=len(urls), desc="Processing files") as pbar:
            processor = self.FileProcessor(output_dir, self.MAX_PROCESSING_WORKERS, self.QUEUE_SIZE, pbar, self)
            processor.start_processing_workers()

            semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_DOWNLOADS)
            decompression_pool = ThreadPoolExecutor(max_workers=self.MAX_DECOMPRESSION_WORKERS)

            connector = aiohttp.TCPConnector(
                limit=self.MAX_CONCURRENT_DOWNLOADS,
                force_close=False,
                ssl=ssl.create_default_context(),
                ttl_dns_cache=300,
                keepalive_timeout=60
            )

            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=3600)) as session:
                tasks = [self.download_and_process(session, url, semaphore, decompression_pool, output_dir, processor) for url in urls]
                await asyncio.gather(*tasks, return_exceptions=True)

            processor.processing_queue.join()
            processor.stop_workers()
            decompression_pool.shutdown()

    async def download_all_pages(self, submission_type=None, cik=None, filing_date=None, output_dir="download"):
        connector = aiohttp.TCPConnector(ssl=ssl.create_default_context())
        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                urls, pagination = await self._fetch_submissions(session, submission_type=submission_type, cik=cik, filing_date=filing_date, page=1)
                total_urls = urls.copy()
                current_page = 1
                
                while pagination.get('hasMore', False):
                    current_page += 1
                    more_urls, pagination = await self._fetch_submissions(session, submission_type=submission_type, cik=cik, filing_date=filing_date, page=current_page)
                    total_urls.extend(more_urls)
                
                if total_urls:
                    start_time = time.time()
                    await self.process_batch(total_urls, output_dir)
                    elapsed_time = time.time() - start_time
                    print(f"\nProcessing completed in {elapsed_time:.2f} seconds")
                else:
                    print("No submissions found matching the criteria")
                    
            except InsufficientBalanceError as e:
                error_msg = {
                    "error": "insufficient_balance",
                    "required_cost": e.required_cost,
                    "current_balance": e.current_balance,
                    "total_urls": e.total_urls,
                    "additional_funds_needed": e.required_cost - e.current_balance
                }
                self._log_error(output_dir, "balance_check", error_msg)
                return

    def download_submissions(self, submission_type=None, cik=None, ticker=None, filing_date=None, output_dir="download"):
        if self.api_key is None:
            raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")

        if filing_date is not None:
            if isinstance(filing_date, str):
                filing_date = int(filing_date.replace('-', ''))
            elif isinstance(filing_date, list):
                filing_date = [int(x.replace('-', '')) for x in filing_date]
            elif isinstance(filing_date, tuple):
                filing_date = (int(filing_date[0].replace('-', '')), int(filing_date[1].replace('-', '')))

        if ticker is not None:
            cik = identifier_to_cik(ticker)

        if cik is not None:
            if isinstance(cik, str):
                cik = [int(cik)]
            elif isinstance(cik, int):
                cik = [cik]
            elif isinstance(cik, list):
                cik = [int(x) for x in cik]

        async def _download():
            try:
                await self.download_all_pages(submission_type=submission_type, cik=cik, filing_date=filing_date, output_dir=output_dir)
            except Exception as e:
                if not isinstance(e, InsufficientBalanceError):
                    self._log_error(output_dir, "download_error", str(e))

        asyncio.run(_download())
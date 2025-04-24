import os
import asyncio
import aiohttp
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
from .query import query
from os import cpu_count
from ..submission import Submission



class Downloader:
    def __init__(self, api_key=None):
        self.BASE_URL = "https://library.datamule.xyz/original/nc/"
        self.CHUNK_SIZE = 2 * 1024 * 1024
        self.MAX_CONCURRENT_DOWNLOADS = 100
        self.MAX_DECOMPRESSION_WORKERS = cpu_count()
        self.MAX_PROCESSING_WORKERS = cpu_count()
        self.QUEUE_SIZE = 10
        if api_key is not None:
            self._api_key = api_key
        # Create a shared event loop for async operations
        self.loop = asyncio.new_event_loop()
        # Create a thread to run the event loop
        self.loop_thread = Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
        # Create a queue for async tasks
        self.async_queue = Queue()
        
    def _run_event_loop(self):
        """Run the event loop in a separate thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def _run_coroutine(self, coro):
        """Run a coroutine in the event loop and return its result"""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

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

    class FileProcessor:
        def __init__(self, output_dir, max_workers, queue_size, pbar, downloader, keep_document_types=None):
            self.processing_queue = Queue(maxsize=queue_size)
            self.should_stop = False
            self.processing_workers = []
            self.output_dir = output_dir
            self.max_workers = max_workers
            self.batch_size = 50
            self.pbar = pbar
            self.downloader = downloader
            self.keep_document_types = keep_document_types

        def start_processing_workers(self):
            for _ in range(self.max_workers):
                worker = Thread(target=self._processing_worker)
                worker.daemon = True
                worker.start()
                self.processing_workers.append(worker)

        def _process_file(self, item):
            filename, content = item
            try:
                submission = Submission(sgml_content=content, keep_document_types=self.keep_document_types)
                # Use the shared event loop to run save_async
                self.downloader._run_coroutine(submission.save_async(output_dir=self.output_dir))
                self.pbar.update(1)
            except Exception as e:
                accession_dir = os.path.join(self.output_dir, filename.split('.')[0])  
                if os.path.exists(accession_dir):
                    shutil.rmtree(accession_dir)
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

    async def process_batch(self, urls, output_dir, keep_document_types=None):
        os.makedirs(output_dir, exist_ok=True)
        
        with tqdm(total=len(urls), desc="Processing files") as pbar:
            processor = self.FileProcessor(output_dir, self.MAX_PROCESSING_WORKERS, self.QUEUE_SIZE, pbar, self, keep_document_types=keep_document_types)
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

            # timeout should be max 30s.
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=30)) as session:
                tasks = [self.download_and_process(session, url, semaphore, decompression_pool, output_dir, processor) for url in urls]
                await asyncio.gather(*tasks, return_exceptions=True)

            processor.processing_queue.join()
            processor.stop_workers()
            decompression_pool.shutdown()

    def download(self, submission_type=None, cik=None, filing_date=None, output_dir="downloads", accession_numbers=None, keep_document_types=None):
        """
        Query SEC filings and download/process them.
        
        Parameters:
        - submission_type: Filing type(s), string or list (e.g., '10-K', ['10-K', '10-Q'])
        - cik: Company CIK number(s), string, int, or list
        - filing_date: Filing date(s), string, list, or tuple of (start_date, end_date)
        - output_dir: Directory to save downloaded files
        - accession_numbers: List of specific accession numbers to download
        - keep_document_types: List of document types to keep (e.g., ['10-K', 'EX-10.1'])
        """
        if self.api_key is None:
            raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")

        # Query the SEC filings first - before starting any async operations
        print("Querying SEC filings...")
        filings = query(
            submission_type=submission_type,
            cik=cik,
            filing_date=filing_date,
            api_key=self.api_key
        )
        # After querying but before generating URLs
        if accession_numbers:
            filings = [filing for filing in filings if filing['accession_number'] in accession_numbers]
        
        # Generate URLs from the query results
        
        print(f"Generating URLs for {len(filings)} filings...")
        urls = []
        for item in filings:
            url = f"{self.BASE_URL}{str(item['accession_number']).zfill(18)}.sgml"
            if item['compressed'] == True or item['compressed'] == 'true' or item['compressed'] == 'True':
                url += '.zst'
            urls.append(url)
        
        if not urls:
            print("No submissions found matching the criteria")
            return

        # Remove duplicates
        urls = list(set(urls))
        
        # Now start the async processing
        start_time = time.time()
        
        # Process the batch asynchronously
        asyncio.run(self.process_batch(urls, output_dir, keep_document_types=keep_document_types))
        
        # Calculate and display performance metrics
        elapsed_time = time.time() - start_time
        print(f"\nProcessing completed in {elapsed_time:.2f} seconds")
        print(f"Processing speed: {len(urls)/elapsed_time:.2f} files/second")
    
    def __del__(self):
        """Cleanup when the downloader is garbage collected"""
        if hasattr(self, 'loop') and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)


def download(submission_type=None, cik=None, filing_date=None, api_key=None, output_dir="downloads", accession_numbers=None, keep_document_types=None):
    """
    Query SEC filings and download/process them.
    
    Parameters:
    - submission_type: Filing type(s), string or list (e.g., '10-K', ['10-K', '10-Q'])
    - cik: Company CIK number(s), string, int, or list
    - filing_date: Filing date(s), string, list, or tuple of (start_date, end_date)
    - api_key: API key for datamule service (optional if DATAMULE_API_KEY env var is set)
    - output_dir: Directory to save downloaded files
    - accession_numbers: List of specific accession numbers to download
    - keep_document_types: List of document types to keep (e.g., ['10-K', 'EX-10.1'])
    """
    if accession_numbers:
        accession_numbers = [int(str(x).replace('-', '')) for x in accession_numbers]
    # check if acc no is empty list
    elif accession_numbers == []:
        raise ValueError("Applied filter resulted in empty accession numbers list")
    downloader = Downloader(api_key=api_key)
    downloader.download(
        submission_type=submission_type,
        cik=cik,
        filing_date=filing_date,
        output_dir=output_dir,
        accession_numbers=accession_numbers,
        keep_document_types=keep_document_types
    )
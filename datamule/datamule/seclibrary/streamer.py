import os
import asyncio
import aiohttp
import ssl
import zstandard as zstd
import io
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from tqdm import tqdm
from .query import Query

class Streamer:
    def __init__(self, api_key=None):
        self.BASE_URL = "https://library.datamule.xyz/original/nc/"
        self.CHUNK_SIZE = 2 * 1024 * 1024  # 2MB chunks for streaming
        self.MAX_CONCURRENT_DOWNLOADS = 10
        self.MAX_DECOMPRESSION_WORKERS = 8
        self._api_key = api_key
        self.total_processed = 0
        self.success_count = 0
        self.error_count = 0
        self.start_time = None

    @property
    def api_key(self):
        return getattr(self, '_api_key', None) or os.getenv('DATAMULE_API_KEY')

    @api_key.setter
    def api_key(self, value):
        if not value:
            raise ValueError("API key cannot be empty")
        self._api_key = value

    async def _decompress_content(self, compressed_data, executor):
        """Decompress zstandard compressed content using streaming approach from premiumdownloader"""
        try:
            loop = asyncio.get_running_loop()
            
            # Run decompression in a separate thread to avoid blocking the event loop
            decompressed_data = await loop.run_in_executor(
                executor,
                self._decompress_with_streaming,
                compressed_data
            )
            
            return decompressed_data
        except Exception as e:
            raise ValueError(f"Failed to decompress content: {str(e)}")
    
    def _decompress_with_streaming(self, compressed_data):
        """Use streaming decompression following premiumdownloader pattern"""
        dctx = zstd.ZstdDecompressor()
        input_buffer = io.BytesIO(compressed_data)
        decompressed_content = io.BytesIO()
        
        try:
            with dctx.stream_reader(input_buffer) as reader:
                shutil.copyfileobj(reader, decompressed_content)
                
            return decompressed_content.getvalue().decode('utf-8')
        except Exception as e:
            raise ValueError(f"Streaming decompression error: {str(e)}")
        finally:
            try:
                input_buffer.close()
                decompressed_content.close()
            except:
                pass

    async def _download_submission(self, session, accession_number, semaphore, decompression_pool):
        """Download a single submission file"""
        async with semaphore:
            # Ensure accession number is padded to 18 digits
            padded_accession = str(accession_number).zfill(18)
            
            # Try with .zst extension first (compressed), fallback to uncompressed
            for is_compressed in [True, False]:
                extension = ".sgml.zst" if is_compressed else ".sgml"
                url = f"{self.BASE_URL}{padded_accession}{extension}"
                
                headers = {
                    'Connection': 'keep-alive',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Authorization': f'Bearer {self.api_key}'
                }
                
                try:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            # Stream the response content
                            chunks = []
                            async for chunk in response.content.iter_chunked(self.CHUNK_SIZE):
                                chunks.append(chunk)
                            
                            data = b''.join(chunks)
                            
                            # If compressed, decompress the content
                            if is_compressed:
                                content = await self._decompress_content(data, decompression_pool)
                            else:
                                content = data.decode('utf-8')
                                
                            return {
                                'accession_number': accession_number,
                                'content': content,
                                'success': True
                            }
                        # If file not found with .zst extension, try without it
                        elif response.status == 404 and is_compressed:
                            continue
                        elif response.status == 401:
                            return {
                                'accession_number': accession_number,
                                'error': "Authentication failed: Invalid API key",
                                'success': False
                            }
                        else:
                            return {
                                'accession_number': accession_number,
                                'error': f"Download failed: Status {response.status}",
                                'success': False
                            }
                except Exception as e:
                    return {
                        'accession_number': accession_number,
                        'error': str(e),
                        'success': False
                    }
            
            # If we've tried both extensions and neither worked
            return {
                'accession_number': accession_number,
                'error': "File not found with either .sgml.zst or .sgml extension",
                'success': False
            }

    async def _process_query_result(self, item, session, semaphore, decompression_pool, callback):
        """Process a single query result item"""
        accession_number = item.get('accession_number')
        if not accession_number:
            return
            
        result = await self._download_submission(session, accession_number, semaphore, decompression_pool)
        
        self.total_processed += 1
        if result['success']:
            self.success_count += 1
            if callback:
                try:
                    await callback(result)
                except Exception as e:
                    print(f"Error in callback for accession {accession_number}: {str(e)}")
        else:
            self.error_count += 1
            print(f"Error downloading {accession_number}: {result.get('error', 'Unknown error')}")

    def _query_callback(self, item, session, semaphore, decompression_pool, callback, progress_bar):
        """Callback function for Query that processes each item as it arrives"""
        asyncio.create_task(self._handle_query_item(item, session, semaphore, decompression_pool, callback, progress_bar))
        
    async def _handle_query_item(self, item, session, semaphore, decompression_pool, callback, progress_bar):
        """Asynchronously handle a query item"""
        await self._process_query_result(item, session, semaphore, decompression_pool, callback)
        if progress_bar:
            progress_bar.update(1)
            progress_bar.set_postfix_str(f"success={self.success_count} | errors={self.error_count}")

    async def stream(self, submission_type=None, cik=None, filing_date=None, callback=None, show_progress=True):
        """
        Stream SEC filings directly into memory and process them with the provided callback.
        
        Parameters:
        - submission_type: Filing type(s), can be string or list (e.g., '10-K', ['10-K', '10-Q'])
        - cik: Company CIK number(s), can be string, int, or list
        - filing_date: Filing date(s), can be string, list, or tuple of (start_date, end_date)
        - callback: Async function to process each result as it's retrieved
                    Function signature: async def callback(result) where result is a dict with
                    keys 'accession_number', 'content', and 'success'
        - show_progress: Whether to display a progress bar (default: True)
        
        Returns:
        - Dict with summary statistics
        """
        if self.api_key is None:
            raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")
        
        self.start_time = time.time()
        self.total_processed = 0
        self.success_count = 0
        self.error_count = 0
        
        # Create connection pool with SSL context
        connector = aiohttp.TCPConnector(
            limit=self.MAX_CONCURRENT_DOWNLOADS,
            force_close=False,
            ssl=ssl.create_default_context(),
            ttl_dns_cache=300,
            keepalive_timeout=60
        )
        
        # Use a semaphore to limit concurrent downloads
        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_DOWNLOADS)
        
        # Create thread pool for decompression operations
        decompression_pool = ThreadPoolExecutor(max_workers=self.MAX_DECOMPRESSION_WORKERS)
        
        # Use query function to get total filings count for progress bar (without callback)
        from .query import query
        preview_results = await query(
            submission_type=submission_type,
            cik=cik,
            filing_date=filing_date,
            api_key=self.api_key
        )
        total_filings = len(preview_results)
        
        # Initialize progress bar if requested
        progress_bar = None
        if show_progress:
            progress_bar = tqdm(total=total_filings, desc="Streaming filings", unit="file")
        
        try:
            # Create async session for downloads
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=30)) as session:
                # Create a partial function to capture session and other parameters
                stream_callback = lambda item: self._query_callback(
                    item, session, semaphore, decompression_pool, callback, progress_bar
                )
                
                # Run the actual query with our callback using the query function
                from .query import query
                await query(
                    submission_type=submission_type,
                    cik=cik,
                    filing_date=filing_date,
                    callback=stream_callback,
                    api_key=self.api_key
                )
                
                # Wait for all tasks to complete
                tasks = asyncio.all_tasks() - {asyncio.current_task()}
                if tasks:
                    await asyncio.gather(*tasks)
        
        finally:
            # Clean up resources
            if progress_bar:
                progress_bar.close()
            decompression_pool.shutdown()
        
        # Calculate elapsed time and return summary statistics
        elapsed_time = time.time() - self.start_time
        summary = {
            "total_filings": total_filings,
            "processed": self.total_processed,
            "success": self.success_count,
            "errors": self.error_count,
            "elapsed_time": elapsed_time
        }
        
        # Print summary
        print("\nStreaming complete:")
        print(f"- Processed {self.total_processed} of {total_filings} filings")
        print(f"- Success: {self.success_count}, Errors: {self.error_count}")
        print(f"- Total time: {elapsed_time:.1f} seconds")
        
        return summary

def stream(submission_type=None, cik=None, filing_date=None, callback=None, show_progress=True, api_key=None):
    """
    Stream SEC filings with optional filtering and process them with the provided callback
    
    Parameters:
    - submission_type: Filing type(s), can be string or list (e.g., '10-K', ['10-K', '10-Q'])
    - cik: Company CIK number(s), can be string, int, or list
    - filing_date: Filing date(s), can be string, list, or tuple of (start_date, end_date)
    - callback: Async function to process each result as it's retrieved
                Function signature: async def callback(result) where result is a dict with
                keys 'accession_number', 'content', and 'success'
    - show_progress: Whether to display a progress bar (default: True)
    - api_key: Optional API key (can also use DATAMULE_API_KEY environment variable)
    
    Returns:
    - Dict with summary statistics
    """
    # Create a Streamer instance
    streamer = Streamer(api_key=api_key)
    
    # Run the streaming operation and return results
    return asyncio.run(streamer.stream(
        submission_type=submission_type,
        cik=cik,
        filing_date=filing_date,
        callback=callback,
        show_progress=show_progress
    ))
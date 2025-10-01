import asyncio
from urllib.parse import urlencode
from tqdm import tqdm
import re

from .eftsquery import EFTSQuery


# This is to fix some broken SEC URLS. There's a better way to do this, but this is a quick fix.
def fix_filing_url(url):
    match_suffix = re.search(r'/(\d{4})\.(.+?)$', url)
    if match_suffix:
        suffix_number = match_suffix.group(1)
        file_ext = match_suffix.group(2)
        match_accession = re.search(r'/(\d{18})/', url)
        if match_accession:
            accession_number = match_accession.group(1)
            formatted_accession_number = f"{accession_number[:10]}-{accession_number[10:12]}-{accession_number[12:]}"
            new_url = url.rsplit('/', 1)[0] + f'/{formatted_accession_number}-{suffix_number}.{file_ext}'
            return new_url
    return url

class Streamer(EFTSQuery):
    def __init__(self, requests_per_second=5.0, document_callback=None, accession_numbers=None,skip_accession_numbers=None, quiet=False):
        super().__init__(requests_per_second=requests_per_second, quiet=quiet)
        self.document_callback = document_callback
        self.document_queue = asyncio.Queue()
        self.download_in_progress = asyncio.Event()
        self.query_paused = asyncio.Event()
        self.document_pbar = None
        self.document_workers = []
        self.documents_processed = 0
        self.total_documents = 0
        self.accession_numbers = accession_numbers
        self.skip_accession_numbers = skip_accession_numbers
        self.skipped_documents = 0
        
    async def _fetch_worker(self):
        """Override the parent class worker to implement pause/resume"""
        while True:
            try:
                # Check if we should pause for document downloads
                if self.query_paused.is_set():
                    # Wait until downloads are done and we're resumed
                    await self.query_paused.wait()
                    
                params, from_val, size_val, callback = await self.fetch_queue.get()
                
                url = f"{self.base_url}?{urlencode(params, doseq=True)}&from={from_val}&size={size_val}"
                
                try:
                    data = await self._fetch_json(url)
                    if 'hits' in data:
                        hits = data['hits']['hits']
                        if self.pbar:
                            self.pbar.update(len(hits))
                        if callback:
                            await callback(hits)
                    self.fetch_queue.task_done()
                except Exception as e:
                    if not self.quiet:
                        print(f"\nError fetching {url}: {str(e)}")
                    self.fetch_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                if not self.quiet:
                    print(f"\nWorker error: {str(e)}")
                self.fetch_queue.task_done()

    def _construct_submission_url(self, hit):
        """Construct the URL for retrieving the actual submission"""
        try:
            # Extract CIK from the hit
            cik = hit['_source']['ciks'][0]
            
            # Extract accession number from _id (format: accno:file.txt)
            accno_w_dash = hit['_id'].split(':')[0]
            accno_no_dash = accno_w_dash.replace('-', '')
            
            # Check if we should filter by accession numbers
            if self.accession_numbers is not None and accno_w_dash not in self.accession_numbers:
                return None, None, None
            
            if self.skip_accession_numbers is not None and accno_no_dash in self.skip_accession_numbers:
                return None, None, None
            
            # Construct the URL
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accno_no_dash}/{accno_w_dash}.txt"
            url = fix_filing_url(url)
            
            return url, cik, accno_w_dash
        except (KeyError, IndexError) as e:
            if not self.quiet:
                print(f"Error constructing URL for hit: {hit}. Error: {str(e)}")
            return None, None, None

    async def _document_download_worker(self):
        """Worker to download actual filing documents"""
        while True:
            try:
                hit, doc_url, cik, accno = await self.document_queue.get()
                
                try:
                    # Use the same rate limiter as the EFTS queries
                    async with self.limiter:
                        async with self.session.get(doc_url) as response:
                            response.raise_for_status()
                            content = await response.read()
                            
                            # Update rate monitor
                            await self.rate_monitor.add_request(len(content))
                            
                            # Call document callback with content in memory
                            if self.document_callback:
                                await self.document_callback(hit, content, cik, accno, doc_url)
                            
                            # Update progress bar
                            if self.document_pbar:
                                self.document_pbar.update(1)
                                self.documents_processed += 1
                            
                    self.document_queue.task_done()
                except Exception as e:
                    if not self.quiet:
                        print(f"\nError streaming document {doc_url}: {str(e)}")
                    self.document_queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                if not self.quiet:
                    print(f"\nDocument worker error: {str(e)}")
                self.document_queue.task_done()

    async def document_download_callback(self, hits):
        """Callback to process EFTS query results and stream submissions"""
        # Pause the EFTS query processing
        self.query_paused.set()
        
        # Signal that document download is in progress
        self.download_in_progress.set()
        
        # Create progress bar for documents if not exists
        if not self.document_pbar and not self.quiet:
            self.document_pbar = tqdm(total=0, desc="Streaming submissions")
        
        # Queue up the documents for download
        for hit in hits:
            doc_url, cik, accno = self._construct_submission_url(hit)
            if doc_url:
                # Update document progress bar total
                if self.document_pbar:
                    self.document_pbar.total += 1
                self.total_documents += 1
                
                # Add to download queue
                await self.document_queue.put((hit, doc_url, cik, accno))
            elif accno is None and self.accession_numbers is not None:
                # Document was skipped due to accession number filter
                self.skipped_documents += 1
        
        # Wait for all documents to be downloaded
        await self.document_queue.join()
        
        # Resume EFTS query processing
        self.query_paused.clear()
        
        # Signal that document download is complete
        self.download_in_progress.clear()

    async def stream(self, cik=None, submission_type=None, filing_date=None, location=None, name=None):
        """
        Main method to stream EFTS results and download documents
        
        Parameters:
        cik (str or list): Central Index Key(s) for the company
        submission_type (str or list): Filing form type(s) to filter by
        filing_date (str, tuple, or list): Date or date range to filter by
        location (str): Location code to filter by (e.g., 'CA' for California)
        name (str): Company name to search for (alternative to providing CIK)
        
        Returns:
        list: List of all EFTS hits processed
        """
        # Create document worker tasks
        self.document_workers = [
            asyncio.create_task(self._document_download_worker()) 
            for _ in range(5)  # Same number as query workers
        ]
        
        # Reset counters
        self.documents_processed = 0
        self.total_documents = 0
        self.skipped_documents = 0
        
        # Run the main query with our document download callback
        results = await self.query(cik, submission_type, filing_date, location, self.document_download_callback, name)
        
        # Make sure all document downloads are complete
        if self.download_in_progress.is_set():
            if not self.quiet:
                print("Waiting for remaining document downloads to complete...")
            await self.document_queue.join()
        
        # Clean up document workers
        for worker in self.document_workers:
            worker.cancel()
        
        await asyncio.gather(*self.document_workers, return_exceptions=True)
        
        # Close document progress bar and don't show a new one
        if self.document_pbar:
            self.document_pbar.close()
            self.document_pbar = None  # Set to None to prevent reuse
        
        if not self.quiet:
            print(f"\n--- Streaming complete: {len(results)} EFTS results processed ---")
            if self.accession_numbers is not None:
                print(f"--- {self.documents_processed} documents downloaded, {self.skipped_documents} skipped due to accession number filter ---")
        
        return results

def stream(cik=None, submission_type=None, filing_date=None, location=None, 
           requests_per_second=5.0, document_callback=None, filtered_accession_numbers=None,skip_accession_numbers=[],
           quiet=False, name=None):
    """
    Stream EFTS results and download documents into memory.
    
    Parameters:
    - cik: CIK number(s) to query for
    - submission_type: Filing type(s) to query for
    - filing_date: Date or date range to query for
    - location: Location code to filter by (e.g., 'CA' for California)
    - requests_per_second: Rate limit for SEC requests (combined EFTS and document downloads)
    - document_callback: Callback function that receives (hit, content, cik, accno, url)
    - accession_numbers: Optional list of accession numbers to filter by
    - quiet: Whether to suppress progress output
    - name: Company name to search for (alternative to providing CIK)
    
    Returns:
    - List of all EFTS hits processed
    
    Example:
    To search by company name:
        results = stream(name="Tesla", submission_type="10-K")
        
    To search by CIK:
        results = stream(cik="1318605", submission_type="10-K")
        
    To search with location filter:
        results = stream(name="Tesla", location="CA", submission_type="10-K")
    """
    
    # Check if acc no is empty list
    if filtered_accession_numbers == []:
        raise ValueError("Applied filter resulted in empty accession numbers list")
    
    async def run_stream():
        streamer = Streamer(
            requests_per_second=requests_per_second, 
            document_callback=document_callback,
            accession_numbers=filtered_accession_numbers,
            skip_accession_numbers=skip_accession_numbers,
            quiet=quiet
        )
        return await streamer.stream(cik, submission_type, filing_date, location, name)
    
    return asyncio.run(run_stream())
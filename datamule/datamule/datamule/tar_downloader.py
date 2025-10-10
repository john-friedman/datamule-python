import os
import asyncio
import aiohttp
from tqdm import tqdm
import time
import ssl
import zstandard as zstd
import io
import json
import tarfile
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from threading import Lock
from os import cpu_count
from .datamule_lookup import datamule_lookup
from ..utils.format_accession import format_accession
from ..providers.providers import SEC_FILINGS_TAR_BUCKET_ENDPOINT

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=logging.getLogger().handlers,
)
logger = logging.getLogger(__name__)


class TarDownloader:
    def __init__(self, api_key=None):
        self.BASE_URL = SEC_FILINGS_TAR_BUCKET_ENDPOINT
        self.CHUNK_SIZE = 2 * 1024 * 1024
        self.MAX_CONCURRENT_DOWNLOADS = 100
        self.MAX_EXTRACTION_WORKERS = cpu_count()
        self.MAX_TAR_WORKERS = cpu_count()
        self.RANGE_MERGE_THRESHOLD = 1024  # Merge ranges if gap <= 1024 bytes
        if api_key is not None:
            self._api_key = api_key
        self.error_log_lock = Lock()

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
        with self.error_log_lock:
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
                logger.error(f"Failed to log error to {error_file}: {str(e)}")

    def _get_document_ranges(self, accession_num, keep_document_types, range_lookup_db=None):
        """
        Get byte ranges for requested document types.
        
        Args:
            accession_num: The accession number
            keep_document_types: List of document types to retrieve
            range_lookup_db: Future database connection for looking up ranges
        
        Returns:
            dict mapping document_type to (start_byte, end_byte)
        """
        if range_lookup_db is not None:
            # Future: Query database for ranges
            # return range_lookup_db.get_ranges(accession_num, keep_document_types)
            pass
        
        # Hardcoded ranges for now
        ranges = {}
        if 'metadata' in keep_document_types:
            # Metadata is always first 128KB
            ranges['metadata'] = (0, 131071)
        
        return ranges
    
    def _merge_ranges(self, ranges):
        """
        Merge overlapping or close ranges.
        
        Args:
            ranges: dict mapping document_type to (start_byte, end_byte)
        
        Returns:
            list of merged (start_byte, end_byte) tuples, sorted
        """
        if not ranges:
            return []
        
        # Extract and sort ranges by start byte
        range_list = sorted(ranges.values(), key=lambda x: x[0])
        
        merged = []
        current_start, current_end = range_list[0]
        
        for start, end in range_list[1:]:
            # Check if ranges overlap or are within merge threshold
            if start <= current_end + self.RANGE_MERGE_THRESHOLD:
                # Merge: extend current range
                current_end = max(current_end, end)
            else:
                # No merge: save current range and start new one
                merged.append((current_start, current_end))
                current_start, current_end = start, end
        
        # Add the last range
        merged.append((current_start, current_end))
        
        return merged
    
    def _build_range_header(self, merged_ranges):
        """
        Build HTTP Range header from merged ranges.
        
        Args:
            merged_ranges: list of (start_byte, end_byte) tuples
        
        Returns:
            Range header string, e.g., "bytes=0-131071,200000-300000"
        """
        if not merged_ranges:
            return None
        
        range_specs = [f"{start}-{end}" for start, end in merged_ranges]
        return f"bytes={','.join(range_specs)}"
    
    def _parse_tar_header(self, header_bytes):
        """
        Parse a 512-byte tar header.
        
        Returns:
            dict with 'name', 'size', or None if invalid header
        """
        if len(header_bytes) < 512:
            return None
        
        # Check if it's a zero block (end of archive)
        if header_bytes == b'\x00' * 512:
            return None
        
        try:
            # Tar header format (POSIX ustar)
            name = header_bytes[0:100].split(b'\x00')[0].decode('utf-8')
            size_str = header_bytes[124:136].split(b'\x00')[0].decode('utf-8').strip()
            
            if not size_str:
                return None
            
            # Size is in octal
            size = int(size_str, 8)
            
            return {
                'name': name,
                'size': size
            }
        except:
            return None
    
    def _extract_files_from_partial_tar(self, tar_bytes):
        """
        Extract files from partial tar data by manually parsing headers.
        
        Args:
            tar_bytes: Raw bytes from partial tar download
        
        Returns:
            list of dicts with 'name' and 'content'
        """
        files = []
        offset = 0
        
        while offset + 512 <= len(tar_bytes):
            # Read header
            header = self._parse_tar_header(tar_bytes[offset:offset+512])
            
            if header is None:
                # End of archive or invalid header
                break
            
            offset += 512  # Move past header
            
            # Calculate file content end and padding
            file_size = header['size']
            content_end = offset + file_size
            
            # Check if we have the full file content
            if content_end > len(tar_bytes):
                # File is truncated, skip it
                break
            
            # Extract file content
            content = tar_bytes[offset:content_end]
            
            files.append({
                'name': os.path.basename(header['name']),
                'content': content
            })
            
            # Move to next 512-byte boundary
            padding = (512 - (file_size % 512)) % 512
            offset = content_end + padding
        
        return files
    
    def _build_filename_to_type_map(self, metadata_content):
        """
        Parse metadata and build a mapping of filename to document type.
        
        Args:
            metadata_content: The metadata.json content as bytes
        
        Returns:
            dict mapping filename to document type
        """
        try:
            metadata = json.loads(metadata_content)
            filename_map = {}
            
            if 'documents' in metadata:
                for doc in metadata['documents']:
                    filename = doc.get('filename')
                    doc_type = doc.get('type')
                    if filename and doc_type:
                        filename_map[filename] = doc_type
            
            return filename_map
        except:
            return {}
    
    def _filter_documents_by_type(self, documents, filename_map, keep_document_types):
        """
        Filter documents based on their type from metadata.
        
        Args:
            documents: List of dicts with 'name' and 'content'
            filename_map: Dict mapping filename to document type
            keep_document_types: List of document types to keep
        
        Returns:
            Filtered list of documents
        """
        if not keep_document_types or not filename_map:
            return documents
        
        # 'metadata' is special - it's already handled separately
        # Filter out 'metadata' from keep_document_types for document filtering
        doc_types_to_keep = [dt for dt in keep_document_types if dt != 'metadata']
        
        if not doc_types_to_keep:
            # Only metadata requested, no other documents
            return []
        
        filtered = []
        for doc in documents:
            doc_type = filename_map.get(doc['name'])
            if doc_type and doc_type in doc_types_to_keep:
                filtered.append(doc)
        
        return filtered
    
    def _decompress_zstd(self, compressed_content):
        """Decompress zstd content"""
        dctx = zstd.ZstdDecompressor()
        return dctx.decompress(compressed_content)

    class TarManager:
        def __init__(self, output_dir, num_tar_files, max_batch_size=1024*1024*1024):
            self.output_dir = output_dir
            self.num_tar_files = num_tar_files
            self.max_batch_size = max_batch_size
            self.tar_files = {}
            self.tar_locks = {}
            self.file_counters = {}
            self.tar_sizes = {}
            self.tar_sequences = {}
            
            for i in range(num_tar_files):
                tar_path = os.path.join(output_dir, f'batch_{i:03d}_001.tar')
                self.tar_files[i] = tarfile.open(tar_path, 'a')
                self.tar_locks[i] = Lock()
                self.file_counters[i] = 0
                self.tar_sizes[i] = 0
                self.tar_sequences[i] = 1
        
        def get_tar_index(self, accession_num):
            return hash(accession_num) % self.num_tar_files
        
        def write_submission(self, accession_num, metadata_content, documents):
            tar_index = self.get_tar_index(accession_num)
            
            submission_size = len(metadata_content) + sum(len(doc['content']) for doc in documents)
            
            with self.tar_locks[tar_index]:
                if self.tar_sizes[tar_index] > 0 and self.tar_sizes[tar_index] + submission_size > self.max_batch_size:
                    tar = self.tar_files[tar_index]
                    tar.close()

                    self.tar_sequences[tar_index] += 1
                    new_tar_path = os.path.join(self.output_dir, f'batch_{tar_index:03d}_{self.tar_sequences[tar_index]:03d}.tar')
                    self.tar_files[tar_index] = tarfile.open(new_tar_path, 'a')
                    self.file_counters[tar_index] = 0
                    self.tar_sizes[tar_index] = 0
                
                tar = self.tar_files[tar_index]
                
                try:
                    # Write metadata
                    tarinfo = tarfile.TarInfo(name=f'{accession_num}/metadata.json')
                    tarinfo.size = len(metadata_content)
                    tar.addfile(tarinfo, io.BytesIO(metadata_content))
                    
                    # Write documents
                    for doc in documents:
                        tarinfo = tarfile.TarInfo(name=f'{accession_num}/{doc["name"]}')
                        tarinfo.size = len(doc['content'])
                        tar.addfile(tarinfo, io.BytesIO(doc['content']))
                    
                    self.file_counters[tar_index] += 1
                    self.tar_sizes[tar_index] += submission_size
                    return True
                    
                except Exception as e:
                    logger.error(f"Error writing {accession_num} to tar {tar_index}: {str(e)}")
                    return False
        
        def close_all(self):
            for i, tar in self.tar_files.items():
                try:
                    tar.close()
                except Exception as e:
                    logger.error(f"Error closing tar {i}: {str(e)}")

    def _parse_multipart_byteranges(self, content, content_type):
        """
        Parse multipart/byteranges response.
        Currently simplified for single-range responses.
        Future: implement full multipart parsing when using database with multiple ranges.
        
        Args:
            content: Response body bytes
            content_type: Content-Type header value
        
        Returns:
            list of (start_byte, end_byte, data) tuples
        """
        # For now, handle single range responses only
        if 'boundary=' not in content_type:
            return [(None, None, content)]
        
        # TODO: Implement full multipart parsing when database returns multiple discontinuous ranges
        return [(None, None, content)]

    def extract_and_process_tar(self, tar_content, filename, tar_manager, output_dir, keep_document_types, is_partial=False):
        """Extract tar file and process its contents"""
        try:
            accession_num = filename.replace('.tar', '').split('/')[-1]
            
            # If partial download (range request), manually parse tar headers
            if is_partial:
                files = self._extract_files_from_partial_tar(tar_content)
                
                if not files:
                    self._log_error(output_dir, filename, "No files found in partial tar")
                    return False
                
                # First file is metadata (never compressed)
                metadata_content = files[0]['content']
                
                # Remaining files are documents (always compressed)
                documents = []
                for file in files[1:]:
                    file['content'] = self._decompress_zstd(file['content'])
                    documents.append(file)
                
                # Build filename to type mapping from metadata
                filename_map = self._build_filename_to_type_map(metadata_content)
                
                # Filter documents based on keep_document_types
                documents = self._filter_documents_by_type(documents, filename_map, keep_document_types)
                
            else:
                # Full download, use tarfile library
                tar_buffer = io.BytesIO(tar_content)
                
                with tarfile.open(fileobj=tar_buffer, mode='r') as tar:
                    members = tar.getmembers()
                    
                    if not members:
                        self._log_error(output_dir, filename, "Empty tar file")
                        return False
                    
                    # Read all files
                    metadata_content = None
                    documents = []
                    
                    for idx, member in enumerate(members):
                        if member.isfile():
                            file_content = tar.extractfile(member).read()
                            
                            if idx == 0:
                                # First file is metadata (never compressed)
                                metadata_content = file_content
                            else:
                                # All other files are documents (always compressed)
                                file_content = self._decompress_zstd(file_content)
                                
                                documents.append({
                                    'name': os.path.basename(member.name),
                                    'content': file_content
                                })
                    
                    if metadata_content is None:
                        self._log_error(output_dir, filename, "No metadata found in tar")
                        return False
                    
                    # Build filename to type mapping and filter
                    if keep_document_types:
                        filename_map = self._build_filename_to_type_map(metadata_content)
                        documents = self._filter_documents_by_type(documents, filename_map, keep_document_types)
                
                tar_buffer.close()
            
            # Write to output tar
            success = tar_manager.write_submission(accession_num, metadata_content, documents)
            
            if not success:
                self._log_error(output_dir, filename, "Failed to write to output tar")
            
            return success
                
        except Exception as e:
            self._log_error(output_dir, filename, f"Tar extraction error: {str(e)}")
            return False

    async def download_and_process(self, session, url, semaphore, extraction_pool, tar_manager, output_dir, pbar, keep_document_types, range_lookup_db=None):
        async with semaphore:
            filename = url.split('/')[-1]
            accession_num = filename.replace('.tar', '').split('/')[-1]

            api_key = self.api_key
            if not api_key:
                raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")

            try:
                headers = {
                    'Connection': 'keep-alive',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Authorization': f'Bearer {api_key}'
                }
                
                # Determine if we need partial download
                range_header = None
                is_partial = False
                if keep_document_types:
                    # Get ranges for requested document types
                    doc_ranges = self._get_document_ranges(accession_num, keep_document_types, range_lookup_db)
                    
                    if doc_ranges:
                        # Merge ranges
                        merged_ranges = self._merge_ranges(doc_ranges)
                        
                        # Build range header
                        range_header = self._build_range_header(merged_ranges)
                        
                        if range_header:
                            headers['Range'] = range_header
                            is_partial = True
                
                async with session.get(url, headers=headers) as response:
                    if response.status in (200, 206):  # 200 = full, 206 = partial
                        content_type = response.headers.get('Content-Type', '')
                        
                        # Read all chunks
                        chunks = []
                        async for chunk in response.content.iter_chunked(self.CHUNK_SIZE):
                            chunks.append(chunk)
                        
                        content = b''.join(chunks)
                        
                        # Handle multipart response if needed
                        if response.status == 206 and 'multipart/byteranges' in content_type:
                            # Parse multipart response
                            parts = self._parse_multipart_byteranges(content, content_type)
                            
                            # Reconstruct tar content from parts
                            tar_content = b''.join(part[2] for part in parts)
                        else:
                            tar_content = content
                        
                        # Process in thread pool
                        loop = asyncio.get_running_loop()
                        success = await loop.run_in_executor(
                            extraction_pool,
                            partial(self.extract_and_process_tar, tar_content, filename, tar_manager, output_dir, keep_document_types, is_partial)
                        )

                        if not success:
                            self._log_error(output_dir, filename, "Failed to process tar file")
                            
                    elif response.status == 401:
                        self._log_error(output_dir, filename, "Authentication failed: Invalid API key")
                        raise ValueError("Invalid API key")
                    else:
                        self._log_error(output_dir, filename, f"Download failed: Status {response.status}")
                        
                    pbar.update(1)
                        
            except Exception as e:
                self._log_error(output_dir, filename, str(e))
                pbar.update(1)

    async def process_batch(self, urls, output_dir, max_batch_size=1024*1024*1024, keep_document_types=[], range_lookup_db=None):
        os.makedirs(output_dir, exist_ok=True)
        
        num_tar_files = min(self.MAX_TAR_WORKERS, len(urls))
        
        tar_manager = self.TarManager(output_dir, num_tar_files, max_batch_size)
        
        try:
            with tqdm(total=len(urls), desc="Downloading tar files") as pbar:
                semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_DOWNLOADS)
                extraction_pool = ThreadPoolExecutor(max_workers=self.MAX_EXTRACTION_WORKERS)

                connector = aiohttp.TCPConnector(
                    limit=self.MAX_CONCURRENT_DOWNLOADS,
                    force_close=False,
                    ssl=ssl.create_default_context(),
                    ttl_dns_cache=300,
                    keepalive_timeout=60
                )

                async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=600)) as session:
                    tasks = [
                        self.download_and_process(
                            session, url, semaphore, extraction_pool,
                            tar_manager, output_dir, pbar, keep_document_types, range_lookup_db
                        ) 
                        for url in urls
                    ]
                    await asyncio.gather(*tasks, return_exceptions=True)

                extraction_pool.shutdown()
                
        finally:
            tar_manager.close_all()

    def download(self, submission_type=None, cik=None, filing_date=None, output_dir="downloads", 
                 filtered_accession_numbers=None, skip_accession_numbers=[], 
                 max_batch_size=1024*1024*1024, accession_numbers=None, keep_document_types=[], range_lookup_db=None):
        if self.api_key is None:
            raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")

        logger.debug("Querying SEC filings...")

        if not accession_numbers:
            filings = datamule_lookup(cik=cik, submission_type=submission_type, filing_date=filing_date, 
                    columns=['accessionNumber'], distinct=True, page_size=25000, quiet=False, api_key=self.api_key)

            if filtered_accession_numbers:
                filtered_accession_numbers = [format_accession(item, 'int') for item in filtered_accession_numbers]
                filings = [filing for filing in filings if filing['accessionNumber'] in filtered_accession_numbers]
            
            if skip_accession_numbers:
                skip_accession_numbers = [format_accession(item, 'int') for item in skip_accession_numbers]
                filings = [filing for filing in filings if filing['accessionNumber'] not in skip_accession_numbers]

            logger.debug(f"Generating URLs for {len(filings)} filings...")
            urls = []
            for item in filings:
                url = f"{self.BASE_URL}{str(item['accessionNumber']).zfill(18)}.tar"
                urls.append(url)
        else:
            urls = []
            for accession in accession_numbers:
                url = f"{self.BASE_URL}{format_accession(accession, 'no-dash').zfill(18)}.tar"
                urls.append(url)
        
        if not urls:
            logger.warning("No submissions found matching the criteria")
            return

        urls = list(set(urls))
        
        start_time = time.time()
        
        asyncio.run(self.process_batch(urls, output_dir, max_batch_size=max_batch_size, keep_document_types=keep_document_types, range_lookup_db=range_lookup_db))
        
        elapsed_time = time.time() - start_time
        logger.debug(f"Processing completed in {elapsed_time:.2f} seconds")
        logger.debug(f"Processing speed: {len(urls)/elapsed_time:.2f} files/second")

    def download_files_using_filename(self, filenames, output_dir="downloads", max_batch_size=1024*1024*1024, keep_document_types=[], range_lookup_db=None):
        if self.api_key is None:
            raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")
        
        if not filenames:
            raise ValueError("No filenames provided")
        
        if not isinstance(filenames, (list, tuple)):
            filenames = [filenames]
        
        for filename in filenames:
            if not isinstance(filename, str):
                raise ValueError(f"Invalid filename type: {type(filename)}. Expected string.")
            if not filename.endswith('.tar'):
                raise ValueError(f"Invalid filename format: {filename}. Expected .tar extension.")
        
        logger.debug(f"Generating URLs for {len(filenames)} files...")
        urls = []
        for filename in filenames:
            url = f"{self.BASE_URL}{filename}"
            urls.append(url)
        
        urls = list(set(urls))
        
        logger.debug(f"Downloading {len(urls)} tar files...")
        
        start_time = time.time()
        
        asyncio.run(self.process_batch(urls, output_dir, max_batch_size=max_batch_size, keep_document_types=keep_document_types, range_lookup_db=range_lookup_db))
        
        elapsed_time = time.time() - start_time
        logger.debug(f"Processing completed in {elapsed_time:.2f} seconds")
        logger.debug(f"Processing speed: {len(urls)/elapsed_time:.2f} files/second")


def download_tar(submission_type=None, cik=None, filing_date=None, api_key=None, output_dir="downloads", 
                 filtered_accession_numbers=None, skip_accession_numbers=[], 
                 max_batch_size=1024*1024*1024, accession_numbers=None, keep_document_types=[], range_lookup_db=None):
    
    if filtered_accession_numbers:
        filtered_accession_numbers = [format_accession(x, 'int') for x in filtered_accession_numbers]
    elif filtered_accession_numbers == []:
        raise ValueError("Applied filter resulted in empty accession numbers list")
    
    downloader = TarDownloader(api_key=api_key)
    downloader.download(
        submission_type=submission_type,
        cik=cik,
        filing_date=filing_date,
        output_dir=output_dir,
        filtered_accession_numbers=filtered_accession_numbers,
        skip_accession_numbers=skip_accession_numbers,
        max_batch_size=max_batch_size,
        accession_numbers=accession_numbers,
        keep_document_types=keep_document_types,
        range_lookup_db=range_lookup_db
    )
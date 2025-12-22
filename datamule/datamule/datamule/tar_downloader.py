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
from secsgml.utils import calculate_documents_locations_in_tar
from ..utils.format_accession import format_accession
from ..providers.providers import SEC_FILINGS_TAR_BUCKET_ENDPOINT
from .datamule_lookup import datamule_lookup
import shutil

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
        self.PROBE_SIZE = 131072  # 128KB
        self.RANGE_MERGE_THRESHOLD = 1024  # Merge ranges if gap <= 1KB
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

    def _filter_metadata_documents(self, metadata_dict, downloaded_document_names, keep_filtered_metadata):
        """
        Filter metadata's documents list to match downloaded documents.
        Mimics the behavior of parse_sgml_content_into_memory's filtering.
        
        Args:
            metadata_dict: Original metadata dictionary with 'documents' list
            downloaded_document_names: Set of document filenames that were actually downloaded
            keep_filtered_metadata: If True, keep all metadata. If False, only keep metadata for downloaded docs.
        
        Returns:
            Filtered metadata dictionary
        """
        if keep_filtered_metadata or 'documents' not in metadata_dict:
            # Keep all metadata entries, just downloaded subset of actual documents
            return metadata_dict
        
        # Filter documents list to only include downloaded documents
        filtered_metadata = metadata_dict.copy()
        filtered_documents = []
        
        for doc in metadata_dict.get('documents', []):
            doc_filename = doc.get('filename', f"{doc.get('sequence', 'unknown')}.txt")
            if doc_filename in downloaded_document_names:
                filtered_documents.append(doc)
        
        filtered_metadata['documents'] = filtered_documents
        return filtered_metadata

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

    def _extract_metadata_from_probe(self, probe_bytes):
        """
        Extract metadata from the 128KB probe.
        
        Returns:
            tuple: (metadata_bytes, metadata_dict, is_complete)
            is_complete: True if entire tar fits in probe
        """
        try:
            # Read first tar header (metadata)
            header = self._parse_tar_header(probe_bytes[0:512])
            
            if not header or 'metadata.json' not in header['name']:
                raise ValueError("First file in tar is not metadata.json")
            
            metadata_size = header['size']
            metadata_start = 512
            metadata_end = metadata_start + metadata_size
            
            # Check if metadata fits in probe
            if metadata_end > len(probe_bytes):
                raise ValueError(f"Metadata size {metadata_size} exceeds probe size")
            
            # Extract metadata bytes
            metadata_bytes = probe_bytes[metadata_start:metadata_end]
            
            # Parse metadata JSON
            metadata_dict = json.loads(metadata_bytes)
            
            # Calculate document positions to determine total tar size
            metadata_with_positions = calculate_documents_locations_in_tar(metadata_dict)
            
            # Get the last document's end position to determine tar size
            if 'documents' in metadata_with_positions and metadata_with_positions['documents']:
                last_doc = metadata_with_positions['documents'][-1]
                # Add padding for last document
                last_doc_end = int(last_doc['secsgml_end_byte'])
                padding = (512 - (last_doc_end % 512)) % 512
                # Add two 512-byte zero blocks for EOF
                total_tar_size = last_doc_end + padding + 1024
            else:
                # Only metadata, no documents
                metadata_padding = (512 - (metadata_end % 512)) % 512
                total_tar_size = metadata_end + metadata_padding + 1024
            
            is_complete = total_tar_size <= self.PROBE_SIZE
            
            return metadata_bytes, metadata_with_positions, is_complete
            
        except Exception as e:
            logger.error(f"Error extracting metadata from probe: {str(e)}")
            raise

    def _extract_documents_from_probe(self, probe_bytes, metadata_with_positions, keep_document_types):
        """
        Extract documents from probe when entire tar fits in 128KB.
        
        Returns:
            list of dicts with 'name' and 'content' (decompressed)
        """
        documents = []
        
        try:
            # Filter documents by type
            wanted_docs = []
            for doc in metadata_with_positions.get('documents', []):
                doc_type = doc.get('type', '')
                if not keep_document_types or doc_type in keep_document_types:
                    wanted_docs.append(doc)
            
            # Extract each wanted document
            for doc in wanted_docs:
                start_byte = int(doc['secsgml_start_byte'])
                end_byte = int(doc['secsgml_end_byte'])
                filename = doc.get('filename', f"{doc['sequence']}.txt")
                
                # Check if document is in probe
                if end_byte > len(probe_bytes):
                    continue
                
                # Extract compressed bytes
                compressed_content = probe_bytes[start_byte:end_byte]
                
                # Decompress (all documents are zstd compressed)
                content = self._decompress_zstd(compressed_content)
                
                documents.append({
                    'name': filename,
                    'content': content
                })
                
        except Exception as e:
            logger.error(f"Error extracting documents from probe: {str(e)}")
            raise
        
        return documents

    def _separate_documents_by_location(self, metadata_with_positions, keep_document_types):
        """
        Separate documents into those in probe vs those beyond probe.
        
        Returns:
            tuple: (docs_in_probe, docs_beyond_probe)
        """
        docs_in_probe = []
        docs_beyond_probe = []
        
        for doc in metadata_with_positions.get('documents', []):
            doc_type = doc.get('type', '')
            
            # Check if we want this document type
            if keep_document_types and doc_type not in keep_document_types:
                continue
            
            doc_info = {
                'name': doc.get('filename', f"{doc['sequence']}.txt"),
                'type': doc_type,
                'start': int(doc['secsgml_start_byte']),
                'end': int(doc['secsgml_end_byte']),
                'size': int(doc.get('secsgml_size_bytes', 0))
            }
            
            # Determine if document is in probe or beyond
            if doc_info['end'] <= self.PROBE_SIZE:
                docs_in_probe.append(doc_info)
            elif doc_info['start'] >= self.PROBE_SIZE:
                docs_beyond_probe.append(doc_info)
            else:
                # Document spans probe boundary - treat as beyond probe
                docs_beyond_probe.append(doc_info)
        
        return docs_in_probe, docs_beyond_probe

    def _extract_documents_from_probe_by_list(self, probe_bytes, docs_in_probe):
        """
        Extract specific documents from probe bytes.
        
        Args:
            probe_bytes: The 128KB probe content
            docs_in_probe: List of document info dicts with absolute positions
        
        Returns:
            list of dicts with 'name' and 'content' (decompressed)
        """
        documents = []
        
        try:
            for doc in docs_in_probe:
                start = doc['start']
                end = doc['end']
                name = doc['name']
                
                logger.debug(f"Extracting from probe: {name} at bytes {start}-{end}")
                
                try:
                    # Extract using absolute positions (no offset needed)
                    compressed_content = probe_bytes[start:end]
                    
                    # Decompress
                    content = self._decompress_zstd(compressed_content)
                    
                    documents.append({
                        'name': name,
                        'content': content
                    })
                except Exception as e:
                    logger.error(f"Failed to extract {name} from probe: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error extracting documents from probe: {str(e)}")
        
        return documents

    def _decompress_zstd(self, compressed_content):
        """Decompress zstd content using stream reader"""
        dctx = zstd.ZstdDecompressor()
        try:
            input_buffer = io.BytesIO(compressed_content)
            decompressed_content = io.BytesIO()
            
            with dctx.stream_reader(input_buffer) as reader:
                shutil.copyfileobj(reader, decompressed_content)
            
            result = decompressed_content.getvalue()
            
            input_buffer.close()
            decompressed_content.close()
            
            return result
        except Exception as e:
            logger.error(f"Decompression error: {str(e)}")
            raise

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

    async def download_and_process(self, session, url, semaphore, extraction_pool, tar_manager, output_dir, pbar, keep_document_types, keep_filtered_metadata):
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
                
                # Step 1: Download 128KB probe
                probe_headers = headers.copy()
                probe_headers['Range'] = f'bytes=0-{self.PROBE_SIZE-1}'
                
                async with session.get(url, headers=probe_headers) as probe_response:
                    if probe_response.status not in (200, 206):
                        self._log_error(output_dir, filename, f"Probe failed: Status {probe_response.status}")
                        pbar.update(1)
                        return
                    
                    probe_chunks = []
                    async for chunk in probe_response.content.iter_chunked(self.CHUNK_SIZE):
                        probe_chunks.append(chunk)
                    probe_bytes = b''.join(probe_chunks)
                
                # Step 2: Extract metadata from probe
                loop = asyncio.get_running_loop()
                metadata_bytes, metadata_with_positions, is_complete = await loop.run_in_executor(
                    extraction_pool,
                    partial(self._extract_metadata_from_probe, probe_bytes)
                )
                
                # Step 3: Decide strategy based on completeness and filtering
                documents = []
                
                if is_complete:
                    # Entire tar fits in 128KB probe
                    logger.debug(f"{filename}: Complete in probe")
                    documents = await loop.run_in_executor(
                        extraction_pool,
                        partial(self._extract_documents_from_probe, probe_bytes, metadata_with_positions, keep_document_types)
                    )
                    
                elif keep_document_types == ['metadata']:
                    # Only metadata requested
                    logger.debug(f"{filename}: Metadata only")
                    documents = []
                    
                else:
                    # Separate documents into probe vs beyond probe
                    docs_in_probe, docs_beyond_probe = self._separate_documents_by_location(
                        metadata_with_positions, keep_document_types
                    )
                    
                    logger.debug(f"{filename}: {len(docs_in_probe)} docs in probe, {len(docs_beyond_probe)} docs beyond")
                    
                    # Extract documents from probe
                    if docs_in_probe:
                        probe_documents = await loop.run_in_executor(
                            extraction_pool,
                            partial(self._extract_documents_from_probe_by_list, probe_bytes, docs_in_probe)
                        )
                        documents.extend(probe_documents)
                    
                    # Download each document beyond probe individually
                    if docs_beyond_probe:
                        for doc in docs_beyond_probe:
                            doc_start = doc['start']
                            doc_end = doc['end']
                            doc_name = doc['name']
                            
                            try:
                                # Single range request for this document
                                doc_range_headers = headers.copy()
                                doc_range_headers['Range'] = f'bytes={doc_start}-{doc_end-1}'
                                
                                logger.debug(f"{filename}: Downloading {doc_name} bytes {doc_start}-{doc_end-1}")
                                
                                async with session.get(url, headers=doc_range_headers) as doc_response:
                                    if doc_response.status not in (200, 206):
                                        logger.error(f"Failed to download {doc_name}: Status {doc_response.status}")
                                        continue
                                    
                                    doc_chunks = []
                                    async for chunk in doc_response.content.iter_chunked(self.CHUNK_SIZE):
                                        doc_chunks.append(chunk)
                                    doc_content = b''.join(doc_chunks)
                                
                                # Decompress this single document
                                decompressed = await loop.run_in_executor(
                                    extraction_pool,
                                    partial(self._decompress_zstd, doc_content)
                                )
                                
                                documents.append({
                                    'name': doc_name,
                                    'content': decompressed
                                })
                                
                            except Exception as e:
                                logger.error(f"Failed to download/extract {doc_name}: {str(e)}")
                
                # Filter metadata to match downloaded documents
                downloaded_names = {doc['name'] for doc in documents}
                filtered_metadata_dict = self._filter_metadata_documents(
                    metadata_with_positions, 
                    downloaded_names, 
                    keep_filtered_metadata
                )
                filtered_metadata_bytes = json.dumps(filtered_metadata_dict).encode('utf-8')
                
                # Step 4: Write to output tar
                success = await loop.run_in_executor(
                    extraction_pool,
                    partial(tar_manager.write_submission, accession_num, filtered_metadata_bytes, documents)
                )
                
                if not success:
                    self._log_error(output_dir, filename, "Failed to write to output tar")
                
                pbar.update(1)
                        
            except Exception as e:
                self._log_error(output_dir, filename, str(e))
                pbar.update(1)

    async def process_batch(self, urls, output_dir, max_batch_size=1024*1024*1024, keep_document_types=[], keep_filtered_metadata=False):
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
                            tar_manager, output_dir, pbar, keep_document_types, keep_filtered_metadata
                        ) 
                        for url in urls
                    ]
                    await asyncio.gather(*tasks, return_exceptions=True)

                extraction_pool.shutdown()
                
        finally:
            tar_manager.close_all()

    def download(self, accession_numbers, output_dir="downloads", 
                 keep_document_types=[], max_batch_size=1024*1024*1024, keep_filtered_metadata=False):
        """
        Download SEC filings in tar format for the given accession numbers.
        
        Args:
            accession_numbers: List of accession numbers to download
            output_dir: Directory to save downloaded files
            keep_document_types: List of document types to keep (empty = keep all)
            max_batch_size: Maximum size of each batch tar file in bytes
            keep_filtered_metadata: If True, keep metadata for all documents. If False, only keep metadata for downloaded docs.
        """
        if self.api_key is None:
            raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")

        logger.debug(f"Generating URLs for {len(accession_numbers)} filings...")
        
        urls = []
        for accession in accession_numbers:
            url = f"{self.BASE_URL}{format_accession(accession,'no-dash').zfill(18)}.tar"
            urls.append(url)
        
        # Deduplicate URLs
        urls = list(set(urls))
        
        if not urls:
            logger.warning("No submissions found matching the criteria")
            return

        start_time = time.time()
        
        asyncio.run(self.process_batch(
            urls, output_dir, 
            max_batch_size=max_batch_size, 
            keep_document_types=keep_document_types,
            keep_filtered_metadata=keep_filtered_metadata
        ))
        
        elapsed_time = time.time() - start_time
        logger.debug(f"Processing completed in {elapsed_time:.2f} seconds")
        logger.debug(f"Processing speed: {len(urls)/elapsed_time:.2f} files/second")


def download_tar(cik=None, ticker=None, submission_type=None, filing_date=None, 
                 report_date=None, detected_time=None, contains_xbrl=None,
                 document_type=None, filename=None, sequence=None, 
                 api_key=None, output_dir="downloads", 
                 filtered_accession_numbers=None, skip_accession_numbers=None,
                 keep_document_types=[], max_batch_size=1024*1024*1024,
                 keep_filtered_metadata=False, accession_numbers=None, quiet=False, **kwargs):
    """
    Download SEC filings in tar format from DataMule.
    
    If accession_numbers is provided, downloads those directly.
    Otherwise, queries datamule_lookup with the provided filters to get accession numbers.
    """
    
    downloader = TarDownloader(api_key=api_key)

    # Get accession numbers if not provided
    if accession_numbers is None:
        accession_numbers = datamule_lookup(
            cik=cik, 
            ticker=ticker, 
            submission_type=submission_type, 
            filing_date=filing_date, 
            report_date=report_date, 
            detected_time=detected_time,
            contains_xbrl=contains_xbrl, 
            document_type=document_type, 
            filename=filename, 
            sequence=sequence, 
            filtered_accession_numbers=filtered_accession_numbers,
            skip_accession_numbers=skip_accession_numbers,
            quiet=quiet, 
            api_key=api_key,
            provider='datamule-tar',
            **kwargs
        )
        
        if not accession_numbers:
            logger.warning("No submissions found matching the criteria")
            return
    
    # Download the filings
    downloader.download(
        accession_numbers=accession_numbers,
        output_dir=output_dir,
        keep_document_types=keep_document_types,
        max_batch_size=max_batch_size,
        keep_filtered_metadata=keep_filtered_metadata
    )
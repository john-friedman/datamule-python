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
from pathlib import Path
from threading import Lock
from os import cpu_count
from secsgml2.utils import calculate_documents_locations_in_tar
from ..utils.format_accession import format_accession
from ..providers.providers import SEC_FILINGS_ARCHIVE_TAR_ENDPOINT
from .archive_lookup import lookup_archive_sgml, lookup_archive_tar
import shutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=logging.getLogger().handlers,
)
logger = logging.getLogger(__name__)


def _has_filter_value(value):
    if value is None:
        return False
    if isinstance(value, (list, tuple, set)):
        return len(value) > 0
    return True


def _archive_bin_member_alias(member_name):
    # Archive v3 briefly wrote SGML-sliced documents as doc_N.bin.zst.
    normalized_name = member_name[:-4] if member_name.endswith('.zst') else member_name
    if not normalized_name.startswith('doc_') or not normalized_name.endswith('.bin'):
        return None

    sequence = normalized_name[4:-4]
    if not sequence.isdigit():
        return None

    return f"{sequence}.txt"


class TarDownloader:
    def __init__(self, api_key=None):
        self.BASE_URL = SEC_FILINGS_ARCHIVE_TAR_ENDPOINT
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

    def _filter_metadata_documents(self, metadata_dict, downloaded_document_names):
        """
        Filter metadata's documents list to match downloaded documents.
        Mimics the behavior of parse_sgml_content_into_memory's filtering.
        
        Args:
            metadata_dict: Original metadata dictionary with 'documents' list
            downloaded_document_names: Set of document filenames that were actually downloaded
        
        Returns:
            Filtered metadata dictionary
        """
        if 'documents' not in metadata_dict:
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

    def _document_name_from_metadata(self, doc):
        filename = doc.get('filename')
        if filename:
            return filename
        return f"{doc.get('sequence', 'document')}.txt"

    def _extract_submission_from_tar(self, tar_bytes, keep_document_types, wanted_filenames=None):
        metadata_dict = None
        compressed_documents = {}
        wanted_filenames = set(wanted_filenames) if wanted_filenames else None

        with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode='r:*') as archive:
            for member in archive:
                if not member.isfile():
                    continue

                extracted = archive.extractfile(member)
                if extracted is None:
                    continue

                member_name = Path(member.name).name
                if not member_name:
                    continue

                data = extracted.read()
                if member_name == 'metadata.json':
                    metadata_dict = json.loads(data.decode('utf-8'))
                else:
                    compressed_documents[member_name] = data
                    if member_name.endswith('.zst'):
                        compressed_documents[member_name[:-4]] = data
                    alias_name = _archive_bin_member_alias(member_name)
                    if alias_name:
                        compressed_documents[alias_name] = data

        if metadata_dict is None:
            raise ValueError("Archive tar did not contain metadata.json")

        documents = []
        filtered_metadata_documents = []
        keep_types = set(keep_document_types or [])

        for doc in metadata_dict.get('documents', []):
            doc_name = self._document_name_from_metadata(doc)
            if wanted_filenames is not None and doc_name not in wanted_filenames:
                continue
            if keep_types and doc.get('type') not in keep_types:
                continue
            content = compressed_documents.get(doc_name)
            if content is None:
                content = compressed_documents.get(f"{doc_name}.zst")
            if content is None:
                raise FileNotFoundError(
                    f"Document listed in metadata but not found in tar: {doc_name}"
                )

            content = self._decompress_zstd(content)
            documents.append({
                'name': doc_name,
                'content': content,
            })
            filtered_metadata_documents.append(doc)

        filtered_metadata = metadata_dict.copy()
        filtered_metadata['documents'] = filtered_metadata_documents
        metadata_content = json.dumps(filtered_metadata).encode('utf-8')
        return metadata_content, documents

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

    async def download_and_process(self, session, spec, semaphore, extraction_pool, tar_manager, output_dir, pbar, keep_document_types):
        async with semaphore:
            url = spec['url']
            filename = url.split('/')[-1]
            accession_num = spec['accession']

            api_key = self.api_key
            if not api_key:
                raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")

            try:
                headers = {
                    'Connection': 'keep-alive',
                    'Accept-Encoding': 'gzip, deflate, br'
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        self._log_error(output_dir, filename, f"Download failed: Status {response.status}")
                        pbar.update(1)
                        return
                    
                    chunks = []
                    async for chunk in response.content.iter_chunked(self.CHUNK_SIZE):
                        chunks.append(chunk)
                    tar_bytes = b''.join(chunks)
                
                loop = asyncio.get_running_loop()
                metadata_bytes, documents = await loop.run_in_executor(
                    extraction_pool,
                    partial(
                        self._extract_submission_from_tar,
                        tar_bytes,
                        keep_document_types,
                        spec.get('wanted_filenames'),
                    )
                )
                
                success = await loop.run_in_executor(
                    extraction_pool,
                    partial(tar_manager.write_submission, accession_num, metadata_bytes, documents)
                )
                
                if not success:
                    self._log_error(output_dir, filename, "Failed to write to output tar")
                
                pbar.update(1)
                        
            except Exception as e:
                self._log_error(output_dir, filename, str(e))
                pbar.update(1)

    async def process_batch(self, specs, output_dir, max_batch_size=1024*1024*1024, keep_document_types=[]):
        os.makedirs(output_dir, exist_ok=True)
        
        num_tar_files = min(self.MAX_TAR_WORKERS, len(specs))
        
        tar_manager = self.TarManager(output_dir, num_tar_files, max_batch_size)
        
        try:
            with tqdm(total=len(specs), desc="Downloading tar files") as pbar:
                semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_DOWNLOADS)
                extraction_pool = ThreadPoolExecutor(max_workers=self.MAX_EXTRACTION_WORKERS)

                connector = aiohttp.TCPConnector(
                    limit=self.MAX_CONCURRENT_DOWNLOADS,
                    force_close=False,
                    ssl=ssl.create_default_context(),
                    ttl_dns_cache=300,
                    keepalive_timeout=60
                )

                # timeout
                async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=60)) as session:
                    tasks = [
                        self.download_and_process(
                            session, spec, semaphore, extraction_pool,
                            tar_manager, output_dir, pbar, keep_document_types
                        ) 
                        for spec in specs
                    ]
                    await asyncio.gather(*tasks, return_exceptions=True)

                extraction_pool.shutdown()
                
        finally:
            tar_manager.close_all()

    def _spec_from_archive_record(self, record):
        filing_date = record.get('filing_date') or record.get('filingDate')
        accession = record.get('accession')
        if filing_date is None or accession is None:
            raise ValueError("Archive lookup record must include filing_date and accession")

        accession = format_accession(accession, 'no-dash')
        return {
            'url': f"{self.BASE_URL}{filing_date}/{accession}.tar",
            'accession': accession,
            'filename': record.get('filename'),
        }

    def download(self, accession_numbers=None, output_dir="downloads", 
                 keep_document_types=[], max_batch_size=1024*1024*1024,
                 archive_records=None):
        """
        Download SEC filings in tar format for the given accession numbers.
        
        Args:
            accession_numbers: List of accession numbers to download
            output_dir: Directory to save downloaded files
            keep_document_types: List of document types to keep (empty = keep all)
            max_batch_size: Maximum size of each batch tar file in bytes
        """
        if self.api_key is None:
            raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")

        if archive_records is None:
            if not accession_numbers:
                logger.warning("No submissions found matching the criteria")
                return
            archive_records = lookup_archive_sgml(
                accession=accession_numbers,
                api_key=self.api_key,
                quiet=True,
            )

        logger.debug(f"Generating URLs for {len(archive_records)} filings...")
        
        specs_by_url = {}
        for record in archive_records:
            spec = self._spec_from_archive_record(record)
            url = spec['url']
            if url not in specs_by_url:
                specs_by_url[url] = {
                    'url': url,
                    'accession': spec['accession'],
                    'wanted_filenames': set(),
                    'has_filename_filter': False,
                }
            if spec.get('filename'):
                specs_by_url[url]['wanted_filenames'].add(spec['filename'])
                specs_by_url[url]['has_filename_filter'] = True

        specs = []
        for spec in specs_by_url.values():
            if not spec.pop('has_filename_filter'):
                spec['wanted_filenames'] = None
            specs.append(spec)
        
        if not specs:
            logger.warning("No submissions found matching the criteria")
            return

        start_time = time.time()
        
        asyncio.run(self.process_batch(
            specs, output_dir,
            max_batch_size=max_batch_size, 
            keep_document_types=keep_document_types
        ))
        
        elapsed_time = time.time() - start_time
        logger.debug(f"Processing completed in {elapsed_time:.2f} seconds")
        logger.debug(f"Processing speed: {len(specs)/elapsed_time:.2f} files/second")


def download_tar(cik=None, ticker=None, submission_type=None, filing_date=None, 
                 report_date=None, detected_time=None, contains_xbrl=None,
                 document_type=None, filename=None, sequence=None, 
                 api_key=None, output_dir="downloads", 
                 filtered_accession_numbers=None, skip_accession_numbers=None,
                 keep_document_types=[], max_batch_size=1024*1024*1024,
                 accession_numbers=None, quiet=False, **kwargs):
    """
    Download SEC filings in tar format from DataMule.
    
    If accession_numbers is provided, resolves those archive records directly.
    Otherwise, queries the v3 archive lookup with the provided filters.
    """
    
    downloader = TarDownloader(api_key=api_key)

    # Get archive coordinates if not provided
    if accession_numbers is not None:
        if not accession_numbers:
            logger.warning("No submissions found matching the criteria")
            return
        archive_records = lookup_archive_sgml(
            accession=accession_numbers,
            quiet=quiet,
            api_key=api_key,
        )
    else:
        document_mode = (
            _has_filter_value(document_type)
            or _has_filter_value(filename)
            or _has_filter_value(sequence)
        )
        lookup_fn = lookup_archive_tar if document_mode else lookup_archive_sgml
        archive_records = lookup_fn(
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
            **kwargs
        )
        
    if not archive_records:
        logger.warning("No submissions found matching the criteria")
        return
    
    # Download the filings
    downloader.download(
        archive_records=archive_records,
        output_dir=output_dir,
        keep_document_types=keep_document_types,
        max_batch_size=max_batch_size
    )

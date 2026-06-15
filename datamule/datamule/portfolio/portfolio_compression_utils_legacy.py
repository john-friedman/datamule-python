import json
import io
import gzip
import zstandard as zstd
import tarfile
import shutil
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from secsgml2.utils import calculate_documents_locations_in_tar

# probably can delete much of this TODO


class CompressionManager:
    
    def compress_portfolio(self, portfolio, compression=None, compression_level=None, threshold=1048576, max_batch_size=1024*1024*1024, max_workers=None):
        """
        Compress all individual submissions into batch tar files.
        
        Args:
            portfolio: Portfolio instance
            compression: None, 'gzip', or 'zstd' for document compression (default: None)
            compression_level: Compression level, if None uses defaults (gzip=6, zstd=3)
            threshold: Size threshold for compressing individual documents (default: 1MB)
            max_batch_size: Maximum size per batch tar file (default: 1GB)
            max_workers: Number of threads for parallel document processing (default: portfolio.MAX_WORKERS)
        """
        if max_workers is None:
            max_workers = portfolio.MAX_WORKERS

        portfolio._close_batch_handles()
            
        if not portfolio.submissions_loaded:
            portfolio._load_submissions()
        
        # Only compress non-batch submissions
        submissions = [s for s in portfolio.submissions if s.batch_tar_path is None]
        
        if not submissions:
            print("No submissions to compress")
            return
        
        print(f"Compressing {len(submissions)} submissions...")
        
        # Set default compression level if not specified
        if compression_level is None:
            compression_level = 6 if compression == 'gzip' else 3
        
        # Group submissions into batches
        current_batch = 0
        current_size = 0
        sequence = 1
        current_tar = None
        
        with tqdm(total=len(submissions), desc="Compressing submissions") as pbar:
            for submission in submissions:
                # Parallel document processing
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    doc_futures = [
                        executor.submit(self._process_document, doc, compression, threshold, compression_level)
                        for doc in submission
                    ]
                    
                    # Collect results maintaining order
                    documents = []
                    compression_list = []
                    for future in doc_futures:
                        content, compression_type = future.result()
                        documents.append(content)
                        compression_list.append(compression_type)
                
                # Calculate submission size
                submission_size = len(submission.metadata.content) + sum(len(doc) for doc in documents)
                
                # Check if we need a new batch tar
                if current_size > 0 and current_size + submission_size > max_batch_size:
                    if current_tar:
                        current_tar.close()
                    sequence += 1
                    current_size = 0
                    current_tar = None
                
                # Create tar if needed
                if current_tar is None:
                    batch_path = portfolio.path / f'batch_{current_batch:03d}_{sequence:03d}.tar'
                    current_tar = tarfile.open(batch_path, 'w')
                
                # Write submission to tar
                self._write_submission_to_tar(
                    current_tar, 
                    submission, 
                    documents, 
                    compression_list,
                    submission.accession
                )
                
                current_size += submission_size
                
                # Remove original submission directory/tar
                if submission.path:
                    if submission.path.is_dir():
                        shutil.rmtree(submission.path)
                    elif submission.path.suffix == '.tar':
                        submission.path.unlink()
                
                pbar.update(1)
        
        # Close final tar
        if current_tar:
            current_tar.close()
        
        # Reload submissions to reflect new batch structure
        portfolio.submissions_loaded = False
        portfolio._load_submissions()
        
        print("Compression complete.")

    def decompress_portfolio(self, portfolio, max_workers=None):
        """
        Decompress all batch tar files back to individual submission directories.
        
        Args:
            portfolio: Portfolio instance
            max_workers: Number of threads for parallel file processing (default: portfolio.MAX_WORKERS)
        """
        # Find all batch tar files
        batch_tars = [f for f in portfolio.path.iterdir() if f.is_file() and 'batch' in f.name and f.suffix == '.tar']
        
        if not batch_tars:
            print("No batch tar files found to decompress")
            return

        if max_workers is None:
            max_workers = min(portfolio.MAX_WORKERS, 4)
        max_workers = max(1, max_workers)
        tar_workers = min(max_workers, len(batch_tars))
        
        print(f"Decompressing {len(batch_tars)} batch tar files with {tar_workers} workers...")
        
        # FIRST: Close all batch tar handles to free the files
        portfolio._close_batch_handles()
        
        total_extracted = 0
        completed_tars = []
        pbar_lock = Lock()
        
        with tqdm(desc="Extracting files", unit="files") as pbar:
            with ThreadPoolExecutor(max_workers=tar_workers) as executor:
                futures = [
                    executor.submit(
                        self._decompress_batch_tar,
                        batch_tar,
                        portfolio.path,
                        max_workers,
                        pbar,
                        pbar_lock
                    )
                    for batch_tar in batch_tars
                ]

                for future in as_completed(futures):
                    batch_tar, extracted_count = future.result()
                    completed_tars.append(batch_tar)
                    total_extracted += extracted_count
                    
        
        # NOW delete the batch tar files after everything is extracted
        for batch_tar in completed_tars:
            batch_tar.unlink()

        
        # Leave submissions lazy; the next iterator/processor call will load the new directory structure.
        portfolio.submissions = []
        portfolio.submissions_loaded = False
        
        print(f"Decompression complete. Extracted {total_extracted} submissions.")

    def _decompress_batch_tar(self, batch_tar, output_path, max_workers, pbar, pbar_lock):
        """Extract one batch tar and post-process extracted files."""
        with tarfile.open(batch_tar, 'r') as tar:
            accession_files = {}
            compressed_paths = []
            for member in tar.getmembers():
                if '/' not in member.name or not member.isfile():
                    continue
                self._validate_tar_member(member)
                accession_dir = member.name.split('/')[0]
                accession_files.setdefault(accession_dir, []).append(member)
                if member.name.endswith(('.gz', '.zst')):
                    compressed_paths.append(output_path / member.name)

            with pbar_lock:
                pbar.total = (pbar.total or 0) + sum(len(members) for members in accession_files.values())
                pbar.refresh()

            for members in accession_files.values():
                for member in members:
                    tar.extract(member, output_path)
                    with pbar_lock:
                        pbar.update(1)

        metadata_paths = [
            output_path / accession_dir / 'metadata.json'
            for accession_dir in accession_files
        ]

        postprocess_workers = min(max_workers, 4)
        with ThreadPoolExecutor(max_workers=postprocess_workers) as executor:
            futures = [
                executor.submit(self._decompress_extracted_file, path)
                for path in compressed_paths
            ]
            futures.extend(
                executor.submit(self._postprocess_metadata_file, path)
                for path in metadata_paths
            )
            for future in as_completed(futures):
                future.result()

        return batch_tar, len(accession_files)

    def _process_document(self, doc, compression, threshold, compression_level):
        """Process a single document: load content and apply compression if needed."""
        content = doc.content
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        # Apply document-level compression if threshold met AND compression is specified
        if compression and len(content) >= threshold:
            if compression == 'gzip':
                content = gzip.compress(content, compresslevel=compression_level)
                compression_type = 'gzip'
            elif compression == 'zstd':
                content = zstd.ZstdCompressor(level=compression_level).compress(content)
                compression_type = 'zstd'
            else:
                compression_type = ''
        else:
            compression_type = ''
        
        return content, compression_type

    def _validate_tar_member(self, member):
        """Reject tar members that would extract outside the portfolio directory."""
        parts = member.name.replace('\\', '/').split('/')
        if member.name.startswith(('/', '\\')) or '..' in parts:
            raise ValueError(f"Unsafe tar member path: {member.name}")

    def _decompress_extracted_file(self, path):
        """Decompress an already extracted legacy-compressed document."""
        if path.suffix == '.gz':
            content = gzip.decompress(path.read_bytes())
        elif path.suffix == '.zst':
            content = zstd.ZstdDecompressor().decompress(path.read_bytes())
        else:
            return

        output_path = path.with_suffix('')
        output_path.write_bytes(content)
        path.unlink()

    def _postprocess_metadata_file(self, metadata_path):
        """Remove tar-specific offsets and align filenames after decompression."""
        if not metadata_path.exists():
            return

        with metadata_path.open('r', encoding='utf-8') as f:
            metadata = json.load(f)

        for doc in metadata.get('documents', []):
            doc.pop('secsgml_start_byte', None)
            doc.pop('secsgml_end_byte', None)

            filename = doc.get('filename', '')
            if filename.endswith('.gz'):
                doc['filename'] = filename[:-3]
            elif filename.endswith('.zst'):
                doc['filename'] = filename[:-4]

        with metadata_path.open('w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
                

    def _write_submission_to_tar(self, tar_handle, submission, documents, compression_list, accession_prefix):
        """Write a submission to a tar file with optional document compression."""
        # Prepare metadata
        metadata = submission.metadata.content.copy()
        
        # Update filenames for compressed documents BEFORE size calculation
        for i, compression in enumerate(compression_list):
            if compression:
                doc = metadata['documents'][i]
                filename = doc.get('filename', doc['sequence'] + '.txt')
                if compression == 'gzip' and not filename.endswith('.gz'):
                    doc['filename'] = filename + '.gz'
                elif compression == 'zstd' and not filename.endswith('.zst'):
                    doc['filename'] = filename + '.zst'
        
        # Add document sizes to metadata for calculate_documents_locations_in_tar
        for i, content in enumerate(documents):
            metadata['documents'][i]['secsgml_size_bytes'] = len(content)
        
        # NOW calculate document positions with the correct filenames
        metadata = calculate_documents_locations_in_tar(metadata)
        
        
        tarinfo = tarfile.TarInfo(name=f'{accession_prefix}/metadata.json')
        tarinfo.size = len(metadata)
        tar_handle.addfile(tarinfo, io.BytesIO(metadata))
        
        # Write documents
        for i, content in enumerate(documents):
            doc = metadata['documents'][i]
            filename = doc.get('filename', doc['sequence'] + '.txt')
            
            tarinfo = tarfile.TarInfo(name=f'{accession_prefix}/{filename}')
            tarinfo.size = len(content)
            tar_handle.addfile(tarinfo, io.BytesIO(content))

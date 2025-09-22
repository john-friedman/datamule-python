import json
import io
import gzip
import zstandard as zstd
import tarfile
import shutil
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from secsgml.utils import bytes_to_str, calculate_documents_locations_in_tar

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
                metadata_str = bytes_to_str(submission.metadata.content, lower=False)
                metadata_json = json.dumps(metadata_str).encode('utf-8')
                submission_size = len(metadata_json) + sum(len(doc) for doc in documents)
                
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
        if max_workers is None:
            max_workers = portfolio.MAX_WORKERS
            
        if not portfolio.submissions_loaded:
            portfolio._load_submissions()
        
        # Find all batch tar files
        batch_tars = [f for f in portfolio.path.iterdir() if f.is_file() and 'batch' in f.name and f.suffix == '.tar']
        
        if not batch_tars:
            print("No batch tar files found to decompress")
            return
        
        print(f"Decompressing {len(batch_tars)} batch tar files...")
        
        # FIRST: Close all batch tar handles to free the files
        portfolio._close_batch_handles()
        
        total_extracted = 0
        
        with tqdm(desc="Decompressing submissions", unit="submissions") as pbar:
            for batch_tar in batch_tars:
                with tarfile.open(batch_tar, 'r') as tar:
                    # Find all accession directories in this tar
                    accession_dirs = set()
                    for member in tar.getmembers():
                        if '/' in member.name:
                            accession_dir = member.name.split('/')[0]
                            accession_dirs.add(accession_dir)
                    
                    # Extract each submission
                    for accession_dir in accession_dirs:
                        output_dir = portfolio.path / accession_dir
                        output_dir.mkdir(exist_ok=True)
                        
                        # Get all files for this accession
                        accession_files = [m for m in tar.getmembers() 
                                            if m.name.startswith(f'{accession_dir}/') and m.isfile()]
                        
                        # Parallel file extraction
                        with ThreadPoolExecutor(max_workers=max_workers) as executor:
                            file_futures = [
                                executor.submit(self._extract_file, member, tar, accession_dir, output_dir)
                                for member in accession_files
                            ]
                            
                            # Wait for all files to be processed
                            for future in as_completed(file_futures):
                                future.result()
                        
                        total_extracted += 1
                        pbar.update(1)
                    
        
        # NOW delete the batch tar files after everything is extracted
        for batch_tar in batch_tars:
            batch_tar.unlink()

        
        # Reload submissions to reflect new directory structure
        portfolio.submissions_loaded = False
        portfolio._load_submissions()
        
        print(f"Decompression complete. Extracted {total_extracted} submissions.")

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

    def _extract_file(self, member, tar, accession_dir, output_dir):
        """Extract and decompress a single file from tar."""
        relative_path = member.name[len(accession_dir)+1:]  # Remove accession prefix
        output_path = output_dir / relative_path
        
        content = tar.extractfile(member).read()
        
        # Handle decompression based on filename
        if relative_path.endswith('.gz'):
            # File MUST be gzipped if it has .gz extension
            content = gzip.decompress(content)
            output_path = output_path.with_suffix('')  # Remove .gz

        elif relative_path.endswith('.zst'):
            # File MUST be zstd compressed if it has .zst extension
            content = zstd.ZstdDecompressor().decompress(content)
            output_path = output_path.with_suffix('')  # Remove .zst
        
        # Special handling for metadata.json
        if output_path.name == 'metadata.json':
            metadata = json.loads(content.decode('utf-8'))
            # Remove tar-specific metadata
            for doc in metadata['documents']:
                doc.pop('secsgml_start_byte', None)
                doc.pop('secsgml_end_byte', None)
                
                # Update filenames to match decompressed files
                filename = doc.get('filename', '')
                if filename.endswith('.gz'):
                    doc['filename'] = filename[:-3]  # Remove .gz
                elif filename.endswith('.zst'):
                    doc['filename'] = filename[:-4]  # Remove .zst
            
            with output_path.open('w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        else:
            # Write document file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open('wb') as f:
                f.write(content)
                

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
        
        # Write metadata
        metadata_str = bytes_to_str(metadata, lower=False)
        metadata_json = json.dumps(metadata_str).encode('utf-8')
        
        tarinfo = tarfile.TarInfo(name=f'{accession_prefix}/metadata.json')
        tarinfo.size = len(metadata_json)
        tar_handle.addfile(tarinfo, io.BytesIO(metadata_json))
        
        # Write documents
        for i, content in enumerate(documents):
            doc = metadata['documents'][i]
            filename = doc.get('filename', doc['sequence'] + '.txt')
            
            tarinfo = tarfile.TarInfo(name=f'{accession_prefix}/{filename}')
            tarinfo.size = len(content)
            tar_handle.addfile(tarinfo, io.BytesIO(content))
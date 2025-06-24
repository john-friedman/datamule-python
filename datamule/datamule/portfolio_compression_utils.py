import json
import io
import gzip
import zstandard as zstd
import tarfile
import shutil
from pathlib import Path
from tqdm import tqdm
from secsgml.utils import bytes_to_str, calculate_documents_locations_in_tar


class CompressionManager:
    
    def compress_portfolio(self, portfolio, compression='zstd', threshold=1048576, max_batch_size=1024*1024*1024):
        """
        Compress all individual submissions into batch tar files.
        
        Args:
            portfolio: Portfolio instance
            compression: 'gzip', 'zstd', or None for document compression
            threshold: Size threshold for compressing individual documents (default: 1MB)
            max_batch_size: Maximum size per batch tar file (default: 1GB)
        """
        if not portfolio.submissions_loaded:
            portfolio._load_submissions()
        
        # Only compress non-batch submissions
        submissions = [s for s in portfolio.submissions if s.batch_tar_path is None]
        
        if not submissions:
            print("No submissions to compress")
            return
        
        print(f"Compressing {len(submissions)} submissions...")
        
        # Set compression level
        compression_level = 6 if compression == 'gzip' else 3
        
        # Group submissions into batches
        current_batch = 0
        current_size = 0
        sequence = 1
        current_tar = None
        
        with tqdm(total=len(submissions), desc="Compressing submissions") as pbar:
            for submission in submissions:
                # Load all documents and apply compression
                documents = []
                compression_list = []
                
                for doc in submission:
                    content = doc.content
                    if isinstance(content, str):
                        content = content.encode('utf-8')
                    
                    # Apply document-level compression if threshold met
                    if compression and len(content) >= threshold:
                        if compression == 'gzip':
                            content = gzip.compress(content, compresslevel=compression_level)
                            compression_list.append('gzip')
                        elif compression == 'zstd':
                            content = zstd.ZstdCompressor(level=compression_level).compress(content)
                            compression_list.append('zstd')
                        else:
                            compression_list.append('')
                    else:
                        compression_list.append('')
                    
                    documents.append(content)
                
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

    def decompress_portfolio(self, portfolio):
        """
        Decompress all batch tar files back to individual submission directories.
        """
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
                try:
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
                            
                            # Extract all files for this accession
                            for member in tar.getmembers():
                                if member.name.startswith(f'{accession_dir}/'):
                                    relative_path = member.name[len(accession_dir)+1:]  # Remove accession prefix
                                    output_path = output_dir / relative_path
                                    
                                    if member.isfile():
                                        content = tar.extractfile(member).read()
                                        
                                        # Handle decompression
                                        if relative_path.endswith('.gz'):
                                            content = gzip.decompress(content)
                                            output_path = output_path.with_suffix('')  # Remove .gz
                                        elif relative_path.endswith('.zst'):
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
                            
                            total_extracted += 1
                            pbar.update(1)
                    
                except Exception as e:
                    print(f"Error decompressing {batch_tar}: {str(e)}")
        
        # NOW delete the batch tar files after everything is extracted
        for batch_tar in batch_tars:
            try:
                batch_tar.unlink()
            except Exception as e:
                print(f"Error deleting {batch_tar}: {str(e)}")
        
        # Reload submissions to reflect new directory structure
        portfolio.submissions_loaded = False
        portfolio._load_submissions()
        
        print(f"Decompression complete. Extracted {total_extracted} submissions.")

    def _write_submission_to_tar(self, tar_handle, submission, documents, compression_list, accession_prefix):
        """Write a submission to a tar file with optional document compression."""
        # Prepare metadata
        metadata = submission.metadata.content.copy()
        
        # Add document sizes to metadata for calculate_documents_locations_in_tar
        for i, content in enumerate(documents):
            metadata['documents'][i]['secsgml_size_bytes'] = len(content)
        
        # Calculate document positions in tar
        metadata = calculate_documents_locations_in_tar(metadata)
        
        # Update filenames for compressed documents
        for i, compression in enumerate(compression_list):
            if compression:
                doc = metadata['documents'][i]
                filename = doc.get('filename', doc['sequence'] + '.txt')
                if compression == 'gzip':
                    doc['filename'] = filename + '.gz'
                elif compression == 'zstd':
                    doc['filename'] = filename + '.zst'
        
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
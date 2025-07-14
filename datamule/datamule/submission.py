from pathlib import Path
import json
from .document.document import Document
from secsgml import parse_sgml_content_into_memory
from secsgml.parse_sgml import transform_metadata_string
from secsgml.utils import bytes_to_str
from .sec.utils import headers
import tarfile
import zstandard as zstd
import gzip
import urllib.request



class Submission:
    def __init__(self, path=None, sgml_content=None, keep_document_types=None,
                 batch_tar_path=None, accession_prefix=None, portfolio_ref=None,url=None):
        
        # Validate parameters
        param_count = sum(x is not None for x in [path, sgml_content, batch_tar_path,url])
        if param_count != 1:
            raise ValueError("Exactly one of path, sgml_content, or batch_tar_path must be provided")
        
        if batch_tar_path is not None and (accession_prefix is None or portfolio_ref is None):
            raise ValueError("batch_tar_path requires both accession_prefix and portfolio_ref")
        
        # Initialize batch tar attributes
        self.batch_tar_path = batch_tar_path
        self.accession_prefix = accession_prefix
        self.portfolio_ref = portfolio_ref
        
        if url is not None or sgml_content is not None:
            if url is not None:
                request = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(request)

                if response.getcode() == 200:
                    sgml_content=response.read()
                else:
                    raise ValueError(f"URL: {url}, Error: {response.getcode()}")

            self.path = None
            metadata, raw_documents = parse_sgml_content_into_memory(sgml_content)
            metadata = bytes_to_str(metadata)

            # standardize metadata
            metadata = transform_metadata_string(metadata)

            self.metadata = Document(type='submission_metadata', content=metadata, extension='.json',filing_date=None,accession=None,path=None)
            # code dupe
            self.accession = self.metadata.content['accession-number']
            self.filing_date= f"{self.metadata.content['filing-date'][:4]}-{self.metadata.content['filing-date'][4:6]}-{self.metadata.content['filing-date'][6:8]}"
    
            self.documents = []
            filtered_metadata_documents = []

            for idx,doc in enumerate(self.metadata.content['documents']):
                type = doc.get('type')
                
                # Keep only specified types
                if keep_document_types is not None and type not in keep_document_types:
                    continue

                # write as txt if not declared
                filename = doc.get('filename','.txt')
                extension = Path(filename).suffix
                self.documents.append(Document(type=type, content=raw_documents[idx], extension=extension,filing_date=self.filing_date,accession=self.accession))

                filtered_metadata_documents.append(doc)
            
            self.metadata.content['documents'] = filtered_metadata_documents

        elif batch_tar_path is not None:
            # Batch tar case
            self.path = None
            
            # Load metadata from batch tar
            with self.portfolio_ref.batch_tar_locks[batch_tar_path]:
                tar_handle = self.portfolio_ref.batch_tar_handles[batch_tar_path]
                metadata_obj = tar_handle.extractfile(f'{accession_prefix}/metadata.json')
                metadata = json.loads(metadata_obj.read().decode('utf-8'))

            # Set metadata path using :: notation
            metadata_path = f"{batch_tar_path}::{accession_prefix}/metadata.json"
            
            # standardize metadata
            metadata = transform_metadata_string(metadata)
            self.metadata = Document(type='submission_metadata', content=metadata, extension='.json',filing_date=None,accession=None,path=metadata_path)
            self.accession = self.metadata.content['accession-number']
            
            # Band-aid fix: some SGML files in the SEC are bad lol, so they have TWO header sections. Will fix post w/ my cleaned archive
            if isinstance(self.accession,list):
                self.accession = self.accession[0]
            #print(f"s: {self.metadata.content['accession-number']} : {batch_tar_path}")
            self.filing_date= f"{self.metadata.content['filing-date'][:4]}-{self.metadata.content['filing-date'][4:6]}-{self.metadata.content['filing-date'][6:8]}"

        elif path is not None:
            self.path = Path(path)  
            if self.path.suffix == '.tar':
                with tarfile.open(self.path,'r') as tar:
                    metadata_obj = tar.extractfile('metadata.json')
                    metadata = json.loads(metadata_obj.read().decode('utf-8'))

                # tarpath
                metadata_path = f"{self.path}::metadata.json"
            else:
                metadata_path = self.path / 'metadata.json'
                with metadata_path.open('r') as f:
                    metadata = json.load(f) 

            # standardize metadata
            metadata = transform_metadata_string(metadata)
            self.metadata = Document(type='submission_metadata', content=metadata, extension='.json',filing_date=None,accession=None,path=metadata_path)
            self.accession = self.metadata.content['accession-number']
            self.filing_date= f"{self.metadata.content['filing-date'][:4]}-{self.metadata.content['filing-date'][4:6]}-{self.metadata.content['filing-date'][6:8]}"

    def _load_document_by_index(self, idx):
        """Load a document by its index in the metadata documents list."""
        doc = self.metadata.content['documents'][idx]
        
        # If loaded from sgml_content, return pre-loaded document
        if self.path is None and self.batch_tar_path is None:
            return self.documents[idx]
        
        # Get filename from metadata - this is the source of truth
        filename = doc.get('filename')
        if filename is None:
            filename = doc['sequence'] + '.txt'

        # Get the base extension (before any compression extension)
        # If filename ends with .gz or .zst, the real extension is before that
        if filename.endswith('.gz'):
            extension = Path(filename[:-3]).suffix
            is_compressed = 'gzip'
        elif filename.endswith('.zst'):
            extension = Path(filename[:-4]).suffix
            is_compressed = 'zstd'
        else:
            extension = Path(filename).suffix
            is_compressed = False

        # Handle batch tar case
        if self.batch_tar_path is not None:
            with self.portfolio_ref.batch_tar_locks[self.batch_tar_path]:
                tar_handle = self.portfolio_ref.batch_tar_handles[self.batch_tar_path]
                
                # Use exact filename from metadata
                tar_path = f'{self.accession_prefix}/{filename}'
                content = tar_handle.extractfile(tar_path).read()
    
                
                # Decompress if needed based on filename extension
                if is_compressed == 'gzip':
                    content = gzip.decompress(content)
                elif is_compressed == 'zstd':
                    content = zstd.ZstdDecompressor().decompress(content)
                
                # Decode text files
                if extension in ['.htm', '.html', '.txt', '.xml']:
                    content = content.decode('utf-8', errors='replace')
                
                document_path = f"{self.batch_tar_path}::{self.accession_prefix}/{filename}"
        
        # Handle regular path case
        else:
            # Check if path is a tar file (old format)
            if self.path.suffix == '.tar':
                with tarfile.open(self.path, 'r') as tar:
                    # Try to extract the file, handling compression
                    try:
                        content = tar.extractfile(filename).read()
                        actual_filename = filename
                    except:
                        try:
                            content = tar.extractfile(filename + '.gz').read()
                            actual_filename = filename + '.gz'
                            is_compressed = 'gzip'
                        except:
                            try:
                                content = tar.extractfile(filename + '.zst').read()
                                actual_filename = filename + '.zst'
                                is_compressed = 'zstd'
                            except:
                                raise FileNotFoundError(f"Document file not found in tar: {filename}")
                    
                    # Decompress if compressed
                    if is_compressed == 'gzip':
                        content = gzip.decompress(content)
                    elif is_compressed == 'zstd':
                        content = zstd.ZstdDecompressor().decompress(content)
                    
                    # Decode text files
                    if extension in ['.htm', '.html', '.txt', '.xml']:
                        content = content.decode('utf-8', errors='replace')
                    
                    document_path = f"{self.path}::{actual_filename}"
            
            else:
                # Regular directory case
                document_path = self.path / filename
                
                if not document_path.exists():
                    raise FileNotFoundError(f"Document file not found: {document_path}")
                
                with document_path.open('rb') as f:
                    content = f.read()
                
                # Decompress if needed based on filename extension
                if is_compressed == 'gzip':
                    content = gzip.decompress(content)
                elif is_compressed == 'zstd':
                    content = zstd.ZstdDecompressor().decompress(content)
                
                # Decode text files
                if extension in ['.htm', '.html', '.txt', '.xml']:
                    content = content.decode('utf-8', errors='replace')

        return Document(
            type=doc['type'], 
            content=content, 
            extension=extension,
            filing_date=self.filing_date,
            accession=self.accession,
            path=document_path
        )
    def __iter__(self):
        """Make Submission iterable by yielding all documents."""
        for idx in range(len(self.metadata.content['documents'])):
            yield self._load_document_by_index(idx)

    def document_type(self, document_type):
        """Yield documents matching the specified type(s)."""
        # Convert single document type to list for consistent handling
        if isinstance(document_type, str):
            document_types = [document_type]
        else:
            document_types = [item for item in document_type]

        for idx, doc in enumerate(self.metadata.content['documents']):
            if doc['type'] in document_types:
                yield self._load_document_by_index(idx)



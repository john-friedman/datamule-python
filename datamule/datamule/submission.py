from pathlib import Path
import json
from .document.document import Document
from secsgml import parse_sgml_content_into_memory
import tarfile
import shutil
import zstandard as zstd
from io import BytesIO
import gzip

class Submission:
    def __init__(self, path=None,sgml_content=None,keep_document_types=None):
        if path is None and sgml_content is None:
            raise ValueError("Either path or sgml_content must be provided")
        if path is not None and sgml_content is not None:
            raise ValueError("Only one of path or sgml_content must be provided")
        
        if sgml_content is not None:
            self.path = None
            metadata, raw_documents = parse_sgml_content_into_memory(sgml_content)
            self.metadata = Document(type='submission_metadata', content=metadata, extension='.json',filing_date=None,accession=None,path=None)
            # code dupe
            self.accession = self.metadata.content['accession-number']
            self.filing_date= f"{self.metadata.content['filing-date'][:4]}-{self.metadata.content['filing-date'][4:6]}-{self.metadata.content['filing-date'][6:8]}"
    
            self.documents = []
            filtered_metadata_documents = []

            for idx,doc in enumerate(self.metadata.content['documents']):
                type = doc.get('type')()
                
                # Keep only specified types
                if keep_document_types is not None and type not in keep_document_types:
                    continue

                # write as txt if not declared
                filename = doc.get('filename','.txt')
                extension = Path(filename).suffix
                self.documents.append(Document(type=type, content=raw_documents[idx], extension=extension,filing_date=self.filing_date,accession=self.accession))

                filtered_metadata_documents.append(doc)
            
            self.metadata.content['documents'] = filtered_metadata_documents

        if path is not None:
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
            self.metadata = Document(type='submission_metadata', content=metadata, extension='.json',filing_date=None,accession=None,path=metadata_path)
            self.accession = self.metadata.content['accession-number']
            self.filing_date= f"{self.metadata.content['filing-date'][:4]}-{self.metadata.content['filing-date'][4:6]}-{self.metadata.content['filing-date'][6:8]}"
    


    def compress(self, compression=None, level=None, threshold=1048576):
        if self.path is None:
            raise ValueError("Compress requires path")
        
        if compression is not None and compression not in ['gzip', 'zstd']:
            raise ValueError("compression must be 'gzip' or 'zstd'")
        
        # Create tar file (replace directory with .tar file)
        tar_path = self.path.with_suffix('.tar')
        
        with tarfile.open(tar_path, 'w') as tar:
            # Add metadata.json first
            metadata_path = self.path / 'metadata.json'
            if metadata_path.exists():
                tar.add(metadata_path, arcname='metadata.json')
            
            # Add documents in order
            for doc in self.metadata.content['documents']:
                filename = doc.get('filename')
                if filename is None:
                    filename = doc['sequence'] + '.txt'
                
                file_path = self.path / filename
                if file_path.exists():
                    file_size = file_path.stat().st_size

                    
                    # Compress if compression specified and over threshold
                    if compression is not None and file_size >= threshold:
                        content = file_path.read_bytes()
                        
                        if compression == 'gzip':
                            compressed_content = gzip.compress(content, compresslevel=level or 6)
                            compressed_filename = filename + '.gz'
                        else:  # zstd
                            cctx = zstd.ZstdCompressor(level=level or 3)
                            compressed_content = cctx.compress(content)
                            compressed_filename = filename + '.zst'
                        
                        # Add compressed file to tar
                        tarinfo = tarfile.TarInfo(name=compressed_filename)
                        tarinfo.size = len(compressed_content)
                        tar.addfile(tarinfo, BytesIO(compressed_content))
                    else:
                        # Add uncompressed file
                        tar.add(file_path, arcname=filename)
        
        # Delete original folder
        shutil.rmtree(self.path)
        
        # Update path to point to new tar file
        self.path = tar_path

    def decompress(self):
        if self.path is None:
            raise ValueError("Decompress requires path")
        elif self.path.suffix != '.tar':
            raise ValueError("Can only decompress tar")
        
        # Create output directory (path without .tar extension)
        output_dir = self.path.with_suffix('')
        output_dir.mkdir(exist_ok=True)
        
        with tarfile.open(self.path, 'r') as tar:
            for member in tar.getmembers():
                if member.isfile():
                    content = tar.extractfile(member).read()
                    
                    # Decompress based on file extension
                    if member.name.endswith('.gz'):
                        content = gzip.decompress(content)
                        output_path = output_dir / member.name[:-3]  # Remove .gz extension
                    elif member.name.endswith('.zst'):
                        dctx = zstd.ZstdDecompressor()
                        content = dctx.decompress(content)
                        output_path = output_dir / member.name[:-4]  # Remove .zst extension
                    else:
                        output_path = output_dir / member.name
                    
                    # Write to output directory
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with output_path.open('wb') as f:
                        f.write(content)

        # delete original file
        self.path.unlink()
        self.path = output_dir

    def _load_document_by_index(self, idx):
        """Load a document by its index in the metadata documents list."""
        doc = self.metadata.content['documents'][idx]
        
        # If loaded from sgml_content, return pre-loaded document
        if self.path is None:
            return self.documents[idx]
        
        # If loaded from path, load document on-demand
        filename = doc.get('filename')
        if filename is None:
            filename = doc['sequence'] + '.txt'

        document_path = self.path / filename
        extension = document_path.suffix

        if self.path.suffix == '.tar':
            with tarfile.open(self.path, 'r') as tar:
                # bandaid fix TODO
                try:
                    content = tar.extractfile(filename).read()
                except:
                    try:
                        content = tar.extractfile(filename+'.gz').read()
                    except:
                        try: 
                            content = tar.extractfile(filename+'.zst').read()
                        except:
                            raise ValueError("Something went wrong with tar")
                # Decompress if compressed
                if filename.endswith('.gz'):
                    content = gzip.decompress(content)
                elif filename.endswith('.zst'):
                    dctx = zstd.ZstdDecompressor()
                    content = dctx.decompress(content)
        else:
            with document_path.open('rb') as f:
                content = f.read()

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
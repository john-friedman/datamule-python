from pathlib import Path
import json
from ..document.document import Document
from secsgml import parse_sgml_content_into_memory
from secsgml.parse_sgml import transform_metadata_string
from secsgml.utils import bytes_to_str
from ..sec.utils import headers
import tarfile
import urllib.request
from secxbrl import parse_inline_xbrl
from company_fundamentals import construct_fundamentals
from decimal import Decimal
from ..utils.format_accession import format_accession
from .tar_submission import tar_submission
import zstandard as zstd

# probably needs rework later
class FundamentalsAccessor:
    def __init__(self, submission):
        self.submission = submission
        self._cache = {}
        self._all_data = None
    
    def __getattr__(self, name):
        # Try as category first
        try:
            if name not in self._cache:
                result = self.submission.parse_fundamentals(categories=[name])
                if result:  # Only cache if we got actual data
                    self._cache[name] = result
                    return result
        except:
            pass
    
        # Fall back to dict behavior
        return getattr(self._get_all_data(), name)
    
    def _get_all_data(self):
        if self._all_data is None:
            self._all_data = self.submission.parse_fundamentals(categories=None)
        return self._all_data
    
    # Make the accessor behave like the underlying data
    def __getitem__(self, key):
        return self._get_all_data()[key]
    
    def __repr__(self):
        return repr(self._get_all_data())
    
    def __str__(self):
        return str(self._get_all_data())
    
    def __iter__(self):
        return iter(self._get_all_data())
    
    def __len__(self):
        return len(self._get_all_data()) if self._get_all_data() else 0
    
    def __bool__(self):
        return bool(self._get_all_data())

class Submission:
    def __init__(self, path=None, sgml_content=None, keep_document_types=None,
                 batch_tar_path=None, accession=None, portfolio_ref=None,url=None):
        
        # get accession number
        # lets just use accesion-prefix, to get around malformed metadata files (1995 has a lot!)
        if path is not None:
            self.accession = format_accession(path.stem,'no-dash')
        elif batch_tar_path is not None:
            self.accession = format_accession(accession,'no-dash')
        elif url is not None:
            if accession is None:
                self.accession = format_accession(Path(url).stem,'no-dash') 
        elif sgml_content is not None:
            if accession is None:
                raise ValueError("If using url or sgml_content, accession must be specified.")
            self.accession = format_accession(accession,'no-dash')
        else:
            raise ValueError("If this appears, please post an issue: https://github.com/john-friedman/datamule-python/issues.")


        # declare vars to be filled later
        self._xbrl = None
        self._fundamentals_cache = {}
        self._tar = None
        self._tar_compression_type = 'zstd'
        self._tar_compression_level = 3
        self._tar_compression_threshold = None
        self._accession_year_2d = None
        self._documents = None
        self._filer_cik = None
        
        # Validate parameters
        param_count = sum(x is not None for x in [path, sgml_content, batch_tar_path,url])
        if param_count != 1:
            raise ValueError("Exactly one of path, sgml_content, or batch_tar_path must be provided")
        
        if batch_tar_path is not None and (self.accession is None or portfolio_ref is None):
            raise ValueError("batch_tar_path requires both accession and portfolio_ref")
        
        # Initialize batch tar attributes
        self.batch_tar_path = batch_tar_path
        self.portfolio_ref = portfolio_ref
        
        # here should set accession either from url or make it a required argument if sgml content
        if url is not None or sgml_content is not None:
            if url is not None:
                request = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(request)

                if response.getcode() == 200:
                    sgml_content=response.read()
                    content_type = response.headers.get('Content-Type', '')
                    if content_type == 'application/zstd':
                        dctx = zstd.ZstdDecompressor()
                        sgml_content = dctx.decompressobj().decompress(sgml_content)
                else:
                    raise ValueError(f"URL: {url}, Error: {response.getcode()}")

            self.path = None
            metadata, raw_documents = parse_sgml_content_into_memory(sgml_content)
            metadata = bytes_to_str(metadata,lower=False)

            # standardize metadata
            metadata = transform_metadata_string(metadata)

            self.metadata = Document(type='submission_metadata', content=metadata, extension='.json',filing_date=None,accession=None,path=None)
            self.filing_date= f"{self.metadata.content['filing-date'][:4]}-{self.metadata.content['filing-date'][4:6]}-{self.metadata.content['filing-date'][6:8]}"
    
            self.documents_obj_list = []
            filtered_metadata_documents = []

            for idx,doc in enumerate(self.metadata.content['documents']):
                type = doc.get('type')
                
                # Keep only specified types
                if keep_document_types is not None and type not in keep_document_types:
                    continue

                # write as txt if not declared
                filename = doc.get('filename','.txt')
                extension = Path(filename).suffix
                self.documents_obj_list.append(Document(type=type, content=raw_documents[idx], extension=extension,filing_date=self.filing_date,accession=self.accession))

                filtered_metadata_documents.append(doc)
            
            self.metadata.content['documents'] = filtered_metadata_documents

        elif batch_tar_path is not None:
            # Batch tar case
            self.path = None
            
            # Load metadata from batch tar
            with self.portfolio_ref.batch_tar_locks[batch_tar_path]:
                tar_handle = self.portfolio_ref.batch_tar_handles[batch_tar_path]
                metadata_obj = tar_handle.extractfile(f'{self.accession}/metadata.json')
                metadata = json.loads(metadata_obj.read().decode('utf-8'))

            # Set metadata path using :: notation
            metadata_path = f"{batch_tar_path}::{self.accession}/metadata.json"
            
            # standardize metadata
            metadata = transform_metadata_string(metadata)
            self.metadata = Document(type='submission_metadata', content=metadata, extension='.json',filing_date=None,accession=None,path=metadata_path)
            
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
            self.filing_date= f"{self.metadata.content['filing-date'][:4]}-{self.metadata.content['filing-date'][4:6]}-{self.metadata.content['filing-date'][6:8]}"


        # booleans
        self._xbrl_bool = any(
                doc['type'] in ('EX-100.INS', 'EX-101.INS') or 
                doc.get('filename', '').endswith('_htm.xml')
                for doc in self.metadata.content['documents']
            )
        
        self._has_fundamentals = self._xbrl_bool
        try:
            self._filer_cik = self.metadata.content.get('filer').get('company-data').get('cik')
        except:
            self._filer_cik = None
        

    # TODO rework for better metadata accessing
    def _load_document_by_index(self, idx):
        """Load a document by its index in the metadata documents list."""
        doc = self.metadata.content['documents'][idx]
        
        # If loaded from sgml_content, return pre-loaded document
        if self.path is None and self.batch_tar_path is None:
            return self.documents_obj_list[idx]
        
        # Get filename from metadata - this is the source of truth
        filename = doc.get('filename')
        if filename is None:
            filename = doc['sequence'] + '.txt'

        extension = Path(filename).suffix
        # Handle batch tar case
        if self.batch_tar_path is not None:
            with self.portfolio_ref.batch_tar_locks[self.batch_tar_path]:
                tar_handle = self.portfolio_ref.batch_tar_handles[self.batch_tar_path]
                
                # Use exact filename from metadata
                tar_path = f'{self.accession}/{filename}'
                content = tar_handle.extractfile(tar_path).read()
    
                
                document_path = f"{self.batch_tar_path}::{self.accession}/{filename}"
        
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
                        raise FileNotFoundError(f"Document file not found in tar: {filename}")
                    
                    document_path = f"{self.path}::{actual_filename}"
            
            else:
                # Regular directory case
                document_path = self.path / filename
                
                if not document_path.exists():
                    raise FileNotFoundError(f"Document file not found: {document_path}")
                
                with document_path.open('rb') as f:
                    content = f.read()
                

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

    def parse_xbrl(self):
        if self._xbrl:
            return
        
        if not self._xbrl_bool:
            print(f"Submission: {self.accession} has no xbrl")
            return
        
        for idx, doc in enumerate(self.metadata.content['documents']):
            if doc['type'] in ['EX-100.INS','EX-101.INS']:
                document = self._load_document_by_index(idx)
                self._xbrl = parse_inline_xbrl(content=document.content,file_type='extracted_inline')
                return  
            
            if doc['filename'].endswith('_htm.xml'):
                document = self._load_document_by_index(idx)
                self._xbrl = parse_inline_xbrl(content=document.content,file_type='extracted_inline')
                return

    @property
    def xbrl(self): 
        if self._xbrl is None:
            self.parse_xbrl()
        return self._xbrl
        
    def parse_fundamentals(self, categories=None):
        # Create cache key based on categories
        categories_key = tuple(sorted(categories)) if categories else 'all'
        
        # Return cached result if available
        if categories_key in self._fundamentals_cache:
            return self._fundamentals_cache[categories_key]
        
        # Use the property to trigger XBRL parsing if needed
        xbrl_data = self.xbrl

        # if no xbrl return None
        if not xbrl_data:
            self._fundamentals_cache[categories_key] = None
            return None
            
        # Transform XBRL records into the format needed by construct_fundamentals
        xbrl = []
        
        for xbrl_record in xbrl_data:
            try:
                # Extract basic fields
                value = xbrl_record.get('_val', None)
                
                taxonomy, name = xbrl_record['_attributes']['name'].split(':')
                

                # Handle scaling if present
                if xbrl_record.get('_attributes', {}).get('scale') is not None:
                    scale = int(xbrl_record['_attributes']['scale'])
                    try:
                        value = str(Decimal(value.replace(',', '')) * (Decimal(10) ** scale))
                    except:
                        pass
                

                # Extract period dates
                period_start_date = None
                period_end_date = None
                
                if xbrl_record.get('_context'):
                    context = xbrl_record['_context']
                    period_start_date = context.get('period_instant') or context.get('period_startdate')
                    period_end_date = context.get('period_enddate')
                else:
                    context = None
                
                # Create record in the format expected by construct_fundamentals
                record = {
                    'taxonomy': taxonomy,
                    'name': name,
                    'value': value,
                    'period_start_date': period_start_date,
                    'period_end_date': period_end_date,
                    'context' : context
                }
                
                xbrl.append(record)
                
            except Exception as e:
                # Skip malformed records
                continue
        
  
        # Call construct_fundamentals with the transformed data
        fundamentals = construct_fundamentals(xbrl, 
                            taxonomy_key='taxonomy', 
                            concept_key='name', 
                            start_date_key='period_start_date', 
                            end_date_key='period_end_date',
                            categories=categories)
        
        # Cache the result
        self._fundamentals_cache[categories_key] = fundamentals
        return fundamentals

    @property
    def fundamentals(self):
        """Access fundamentals via attributes: sub.fundamentals.incomeStatement"""
        if not hasattr(self, '_fundamentals_accessor'):
            self._fundamentals_accessor = FundamentalsAccessor(self)
        return self._fundamentals_accessor
    
    @property
    def tar(self):
        return self._tar_submission().getvalue()
    
    def set_tar_compression(self,compression_type='zstd',level=3,threshold=None):
        self._tar_compression_type = compression_type
        self._tar_compression_level = level
        self._tar_compression_threshold = threshold
    
    def _tar_submission(self):
        if self._tar is not None:
            return self._tar
        else:
            documents_obj_list = self._get_documents_obj_list()
            self._tar = tar_submission(
                documents_obj_list=documents_obj_list,
                metadata=self.metadata.content,
                compression_type=self._tar_compression_type,
                level=self._tar_compression_level,
                threshold=self._tar_compression_threshold
            )
            return self._tar
        
    @property
    def accession_year_2d(self):
        return self._get_accession_year_2d()
    
    def _get_accession_year_2d(self):
        if self._accession_year_2d is not None:
            return self._accession_year_2d
        self._accession_year_2d = format_accession(self.accession,'dash').split('-')[1]
        return self._accession_year_2d
    
    @property
    def documents(self):
        return self._get_documents()
    
    def _get_documents(self):
        if self._documents is not None:
            return self._documents
        
        self._documents = self.metadata.content['documents']
        return self._documents

    def _get_documents_obj_list(self):
        """Get all documents as Document objects"""
        if hasattr(self, 'documents_obj_list'):
            return self.documents_obj_list
        
        # Generate documents_obj_list for batch tar and path cases
        documents_obj_list = []
        for idx in range(len(self.metadata.content['documents'])):
            documents_obj_list.append(self._load_document_by_index(idx))
        
        return documents_obj_list
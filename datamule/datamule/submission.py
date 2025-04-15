from pathlib import Path
import json
from .document.document import Document
from secsgml import parse_sgml_submission_into_memory
from pathlib import Path

class Submission:
    def __init__(self, path=None,sgml_content=None,keep_document_types=None):
        if path is None and sgml_content is None:
            raise ValueError("Either path or sgml_content must be provided")
        if path is not None and sgml_content is not None:
            raise ValueError("Only one of path or sgml_content must be provided")
        
        if sgml_content is not None:
            self.path = None
            self.metadata, raw_documents = parse_sgml_submission_into_memory(sgml_content)
            self.documents = []

            for idx,doc in enumerate(self.metadata['documents']):
                type = doc.get('type')
                
                # Keep only specified types
                if keep_document_types is not None and type not in keep_document_types:
                    continue
                filename = doc.get('filename')
                extension = Path(filename).suffix
                self.documents.append(Document(type=type, content=raw_documents[idx], extension=extension,filing_date=self.filing_date,accession=self.accession))


        if path is not None:
            self.path = Path(path)  
            metadata_path = self.path / 'metadata.json'
            with metadata_path.open('r') as f:
                self.metadata = json.load(f)

        self.accession = self.metadata['accession-number']
        self.filing_date= f"{self.metadata['filing-date'][:4]}-{self.metadata['filing-date'][4:6]}-{self.metadata['filing-date'][6:8]}"
    

    def document_type(self, document_type):
        # Convert single document type to list for consistent handling
        if isinstance(document_type, str):
            document_types = [document_type]
        else:
            document_types = document_type

        for idx,doc in enumerate(self.metadata['documents']):
            if doc['type'] in document_types:
                
                # if loaded from path
                if self.path is not None:
                    filename = doc.get('filename')
                    # oh we need handling here for sequences case
                    if filename is None:
                        filename = doc['sequence'] + '.txt'
                        
                    document_path = self.path / filename
                    extension = document_path.suffix

                    with document_path.open('r') as f:
                        content = f.read()

                    yield Document(type=doc['type'], content=content, extension=extension,filing_date=self.filing_date,accession=self.accession)
                # if loaded from sgml_content
                else:
                    yield self.documents[idx]

    
    def __iter__(self):
        for idx,doc in enumerate(self.metadata['documents']):
            # if loaded from path
            if self.path is not None:
                filename = doc.get('filename')

                # oh we need handling here for sequences case
                if filename is None:
                    filename = doc['sequence'] + '.txt'
                    
                document_path = self.path / filename
                extension = document_path.suffix

                # check if the file exists
                if document_path.exists():
                    with document_path.open('r') as f:
                        content = f.read()

                    yield Document(type=doc['type'], content=content, extension=extension,filing_date=self.filing_date,accession=self.accession)
                else:
                    print(f"Warning: File {document_path} does not exist likely due to keep types in downloading.")

            # if loaded from sgml_content
            else:
                yield self.documents[idx]

    # keep documents by document type
    def keep(self, document_type):
        # Convert single document type to list for consistent handling
        if isinstance(document_type, str):
            document_types = [document_type]
        else:
            document_types = document_type

        if self.path is not None:
            for doc in self.metadata['documents']:
                filename = doc.get('filename')
                type = doc.get('type')
                if type not in document_types:
                    # oh we need handling here for sequences case
                    if filename is None:
                        filename = doc.sequence + '.txt'

                    document_path = self.path / filename
                    # delete the file
                    document_path.unlink()
        else:
            print("Warning: keep() method is only available when loading from path.")
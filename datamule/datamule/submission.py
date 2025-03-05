from pathlib import Path
import json
from .document import Document

class Submission:
    def __init__(self, path):
        self.path = Path(path)
        self._load_metadata()
    
    def _load_metadata(self):
        metadata_path = self.path / 'metadata.json'
        with metadata_path.open('r') as f:
            self.metadata = json.load(f)

    def document_type(self, document_type):
        # Convert single document type to list for consistent handling
        if isinstance(document_type, str):
            document_types = [document_type]
        else:
            document_types = document_type

        for doc in self.metadata['documents']:
            if doc['type'] in document_types:
                filename = doc.get('filename')
                if filename is None:
                    continue
                    
                document_path = self.path / filename
                yield Document(doc['type'], document_path)
    
    def __iter__(self):
        for doc in self.metadata['documents']:
            filename = doc.get('filename')
            if filename is None:
                continue
                
            document_path = self.path / filename
            yield Document(doc['type'], document_path)
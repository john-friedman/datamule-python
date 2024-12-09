from pathlib import Path
import json

class Submission:
    def __init__(self, path):
        self.path = Path(path)
        self._load_metadata()
    
    def _load_metadata(self):
        metadata_path = self.path / 'metadata.json'
        with metadata_path.open('r') as f:
            self.metadata = json.load(f)

    def _load_document(self, filepath):
        with filepath.open('r') as f:
            return f.read()
            
    def keep(self, document_types):
        """Keep files of specified document types, delete others
        Args:
            document_types: string or list of strings representing document types to keep
        """
        # Convert single string to list for consistent handling
        if isinstance(document_types, str):
            document_types = [document_types]
            
        for doc in self.metadata['documents']:
            filename = doc.get('FILENAME')
            if filename is None:
                continue
                
            filepath = self.path / filename
            # Delete if document type isn't in our keep list
            if doc['TYPE'] not in document_types and filepath.exists():
                filepath.unlink()
                
    def drop(self, document_types):
        """Delete files of specified document types, keep others
        Args:
            document_types: string or list of strings representing document types to drop
        """
        # Convert single string to list for consistent handling
        if isinstance(document_types, str):
            document_types = [document_types]
            
        for doc in self.metadata['documents']:
            filename = doc.get('FILENAME')
            if filename is None:
                continue
                
            filepath = self.path / filename
            # Delete if document type is in our drop list
            if doc['TYPE'] in document_types and filepath.exists():
                filepath.unlink()
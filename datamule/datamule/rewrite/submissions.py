from pathlib import Path
import json

class Submission:
   def __init__(self, path):
       self.path = Path(path)
       self.load_metadata()
       self._filter_types = None
   
   def load_metadata(self):
       metadata_path = self.path / 'metadata.json'
       with metadata_path.open('r') as f:
           self.metadata = json.load(f)

   def _load_document(self, filepath):
       with filepath.open('r') as f:
           return f.read()

   def document_type(self, *types):
       """Returns a new Submission instance filtered to specific document types"""
       filtered = Submission(self.path)
       filtered._filter_types = types
       return filtered

   def __iter__(self):
       """Makes Submission iterable, respecting any type filters"""
       for item in self.metadata['documents']:
           if self._filter_types is None or item['DESCRIPTION'] in self._filter_types:
               filename = item.get('FILENAME')
               if filename is None:
                   filename = f"{item['SEQUENCE']}.txt"
               yield self._load_document(self.path / filename)

   def _filter_files(self, doc_types, keep_mode=False):
       """Core function to filter files based on document types
       keep_mode=True for keeping specified types, False for dropping them"""
       
       for item in self.metadata['documents']:
           if item.get('FILENAME') == 'metadata.json':
               continue
               
           # Determine filename
           filename = item.get('FILENAME')
           if filename is None:
               filename = f"{item['SEQUENCE']}.txt"
               
           # Delete file if:
           # - For drop: description is in doc_types
           # - For keep: description is NOT in doc_types
           should_delete = (item['DESCRIPTION'] in doc_types) != keep_mode
           
           if should_delete:
               file_path = self.path / filename
               if file_path.exists():
                   file_path.unlink()

   def drop(self, doc_types):
       """Delete files of specified document types
       Args:
           doc_types: string or list of strings
       """
       if isinstance(doc_types, str):
           doc_types = [doc_types]
       return self._filter_files(doc_types, keep_mode=False)

   def keep(self, doc_types):
       """Keep only files of specified document types
       Args:
           doc_types: string or list of strings
       """
       if isinstance(doc_types, str):
           doc_types = [doc_types]
       return self._filter_files(doc_types, keep_mode=True)
from pathlib import Path
import json
from .document.document import Document
from secsgml import parse_sgml_submission_into_memory
import os
import aiofiles
import tempfile


# # NEW CODE YAY. probably will remove

# def save_metadata_atomically(metadata_file_path, metadata_content):
#     """Save metadata to a JSONL file atomically, works on any filesystem"""
    
#     # Create directory if it doesn't exist
#     os.makedirs(os.path.dirname(metadata_file_path), exist_ok=True)
    
#     # Format the JSON with newline
#     json_str = json.dumps(metadata_content, indent=4) + "\n"
    
#     # Write complete content to a temporary file first
#     fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(metadata_file_path))
#     try:
#         with os.fdopen(fd, 'w') as temp_file:
#             temp_file.write(json_str)
#             temp_file.flush()
#             os.fsync(temp_file.fileno())  # Force write to disk
        
#         # Append the temporary file to the main file
#         with open(metadata_file_path, 'a') as target_file:
#             with open(temp_path, 'r') as temp_read:
#                 content = temp_read.read()
#                 target_file.write(content)
#                 target_file.flush()
#                 os.fsync(target_file.fileno())  # Force write to disk
#     finally:
#         # Clean up the temporary file
#         if os.path.exists(temp_path):
#             os.unlink(temp_path)

# async def save_metadata_atomically_async(metadata_file_path, metadata_content):
#     """Save metadata to a JSONL file atomically in async mode"""
    
#     # Create directory if it doesn't exist
#     os.makedirs(os.path.dirname(metadata_file_path), exist_ok=True)
    
#     # Format the JSON with newline
#     json_str = json.dumps(metadata_content, indent=4) + "\n"
    
#     # Write to a temporary file first
#     fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(metadata_file_path))
#     os.close(fd)  # Close the file descriptor
    
#     try:
#         async with aiofiles.open(temp_path, 'w') as temp_file:
#             await temp_file.write(json_str)
#             await temp_file.flush()
        
#         # Append the temporary file to the main file
#         async with aiofiles.open(metadata_file_path, 'a') as target_file:
#             async with aiofiles.open(temp_path, 'r') as temp_read:
#                 content = await temp_read.read()
#                 await target_file.write(content)
#                 await target_file.flush()
#     finally:
#         # Clean up the temporary file
#         if os.path.exists(temp_path):
#             os.unlink(temp_path)

# # END OF NEW CODE


class Submission:
    def __init__(self, path=None,sgml_content=None,keep_document_types=None):
        if path is None and sgml_content is None:
            raise ValueError("Either path or sgml_content must be provided")
        if path is not None and sgml_content is not None:
            raise ValueError("Only one of path or sgml_content must be provided")
        
        if sgml_content is not None:
            self.path = None
            metadata, raw_documents = parse_sgml_submission_into_memory(sgml_content)
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
                filename = doc.get('filename')
                extension = Path(filename).suffix
                self.documents.append(Document(type=type, content=raw_documents[idx], extension=extension,filing_date=self.filing_date,accession=self.accession))

                filtered_metadata_documents.append(doc)
            
            self.metadata.content['documents'] = filtered_metadata_documents

        if path is not None:
            self.path = Path(path)  
            metadata_path = self.path / 'metadata.json'
            with metadata_path.open('r') as f:
                metadata = json.load(f) 
            self.metadata = Document(type='submission_metadata', content=metadata, extension='.json',filing_date=None,accession=None,path=metadata_path)

            # Code dupe
            self.accession = self.metadata.content['accession-number']
            self.filing_date= f"{self.metadata.content['filing-date'][:4]}-{self.metadata.content['filing-date'][4:6]}-{self.metadata.content['filing-date'][6:8]}"
    



    def document_type(self, document_type):
        # Convert single document type to list for consistent handling
        if isinstance(document_type, str):
            document_types = [document_type]
        else:
            document_types = document_type

        for idx,doc in enumerate(self.metadata.content['documents']):
            if doc['type'] in document_types:
                
                # if loaded from path
                if self.path is not None:
                    filename = doc.get('filename')
                    # oh we need handling here for sequences case
                    if filename is None:
                        filename = doc['sequence'] + '.txt'
                        
                    document_path = self.path / filename
                    extension = document_path.suffix

                    with document_path.open('rb') as f:
                        content = f.read()

                    if extension in ['.htm','.html','.txt','.xml']:
                        content = content.decode('utf-8', errors='replace')

                    yield Document(type=doc['type'], content=content, extension=extension,filing_date=self.filing_date,accession=self.accession,path=document_path)
                # if loaded from sgml_content
                else:
                    yield self.documents[idx]

    
    def __iter__(self):
        for idx,doc in enumerate(self.metadata.content['documents']):
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
                    with document_path.open('rb') as f:
                        content = f.read()

                    if extension in ['.htm','.html','.txt','.xml']:
                        content = content.decode('utf-8', errors='replace')

                    yield Document(type=doc['type'], content=content, extension=extension,filing_date=self.filing_date,accession=self.accession,path=document_path)
                else:
                    print(f"Warning: File {document_path} does not exist likely due to keep types in downloading.")

            # if loaded from sgml_content
            else:
                yield self.documents[idx]




    def save(self, output_dir="filings"):
        file_dir = Path(output_dir) / str(self.accession)
        file_dir.mkdir(parents=True, exist_ok=True)
        
        metadata_path = file_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata.content, f, indent=4)
        
        for idx, doc in enumerate(self.metadata.content['documents']):
            try:
                filename = doc.get('filename')
                if filename is None:
                    filename = f"{doc.get('sequence', idx)}.txt"
            except (KeyError, IndexError):
                filename = f"{idx}.txt"
            
            doc_path = file_dir / filename
            
            if self.path is not None:
                if hasattr(self, 'documents') and self.documents:
                    content = self.documents[idx].content
                else:
                    orig_doc_path = self.path / filename
                    if orig_doc_path.exists():
                        with open(orig_doc_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                    else:
                        print(f"Warning: File {orig_doc_path} does not exist, skipping.")
                        continue
            else:
                content = self.documents[idx].content
            
            if isinstance(content, bytes):
                with open(doc_path, 'wb') as f:
                    f.write(content)
            else:
                with open(doc_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(content)
        
        return file_dir

    async def save_async(self, output_dir="filings"):
        file_dir = Path(output_dir) / str(self.accession)
        os.makedirs(file_dir, exist_ok=True)
        
        metadata_path = file_dir / "metadata.json"
        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(json.dumps(self.metadata.content, indent=4))
        
        for idx, doc in enumerate(self.metadata.content['documents']):
            try:
                filename = doc.get('filename')
                if filename is None:
                    filename = f"{doc.get('sequence', idx)}.txt"
            except (KeyError, IndexError):
                filename = f"{idx}.txt"
            
            doc_path = file_dir / filename
            
            if self.path is not None:
                if hasattr(self, 'documents') and self.documents:
                    content = self.documents[idx].content
                else:
                    orig_doc_path = self.path / filename
                    if orig_doc_path.exists():
                        async with aiofiles.open(orig_doc_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = await f.read()
                    else:
                        print(f"Warning: File {orig_doc_path} does not exist, skipping.")
                        continue
            else:
                content = self.documents[idx].content
            
            if isinstance(content, bytes):
                async with aiofiles.open(doc_path, 'wb') as f:
                    await f.write(content)
            else:
                async with aiofiles.open(doc_path, 'w', encoding='utf-8', errors='replace') as f:
                    await f.write(content)
        
        return file_dir
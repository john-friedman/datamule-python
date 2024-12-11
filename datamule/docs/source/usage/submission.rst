Submission Class
================

A class for managing SEC filing submissions.

Constructor:
------------
- **__init__(self, path)**: Initializes the Submission instance. The `path` is the directory where the submission is stored, and metadata is loaded from `metadata.json`.

Methods:
--------

- **_load_metadata(self)**: Loads metadata from the `metadata.json` file located in the submission's directory.
  
- **keep(self, document_types)**: Keeps files of specified document types, deleting others.
  - **document_types** (`str` or `list` of `str`): Document types to keep.

- **drop(self, document_types)**: Deletes files of specified document types, keeping others.
  - **document_types** (`str` or `list` of `str`): Document types to drop.

- **document_type(self, document_type)**: Yields `Document` instances for the specified document type.
  - **document_type** (`str`): The document type to filter by.
  
Usage Example:
--------------
```python
submission = Submission('path/to/submission')
submission.keep(['10-K', '8-K'])
submission.drop('3')
for doc in submission.document_type('10-K'):
    print(doc)

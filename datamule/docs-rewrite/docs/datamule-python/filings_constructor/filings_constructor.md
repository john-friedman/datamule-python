# Filings Constructor

This is an experimental feature suggested by a compliance officer at a trading firm. User inputs a csv, and gets out the formatted document as expected by the SEC.

User is responsible for validating correctness. This is an open source package.

Quickstart
```python
from datamule import Submission
from datamule.filings_constructor.filings_constructor import construct_document

# GET the file from the SEC
submission = Submission(url="https://www.sec.gov/Archives/edgar/data/1364742/000108636421000038/0001086364-21-000038.txt")

for doc in submission:
    if doc.type == 'INFORMATION TABLE':
        # Save the file to disk for future comparison
        doc.write('information_table_original.xml')
        # Extract the tabular data from the xml file.
        doc.write_csv("13fhr")
        
# Input tabular data
construct_document(input_file='13fhr/information_table.csv', output_file='information_table_new.xml', document_type='INFORMATION TABLE')
```

Currently supports:
- 13F-HR
    - INFORMATION TABLE
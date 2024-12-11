Document
========

Parse and write SEC filings (8-K, 10-Q, 10-K, 13F-HR-INFORMATIONTABLE, Forms 3/4/5, Form D, NPORT-P, SC 13D, SC 13G) to JSON or CSV formats.

Note: It is recommended to access the `Document` class through the `Submission` class, which provides a higher-level interface for managing filings.

.. code-block:: python

   Document(filename, type)

:Parameters:
   ***filename** (*str*) -- Path to the filing file
   ***type** (*str*) -- Filing type (e.g., '8-K', '10-Q', '10-K', '13F-HR-INFORMATIONTABLE', '3', '4', '5', 'D', 'NPORT-P', 'SC 13D', 'SC 13G')

The document's data can be accessed directly through iteration.

.. code-block:: python

   from datamule import Document
   
   doc = Document("myfile.txt", "13F-HR-INFORMATIONTABLE")
   for item in doc:
       print(item)

Data Structure
-------------
* **10-K/10-Q/8-K/SC 13D/SC 13G**: Nested document structure
   * Contains hierarchical sections (document -> item1 -> subitem1a, etc.)
   * CSV output flattens hierarchy with section paths (e.g., "document_item1_subitem1a")
   * Text content preserved in nested format for JSON output

* **13F-HR-INFORMATIONTABLE**: Tabular structure
   * Each row represents a holding
   * Direct mapping to CSV columns
   * No nested flattening required

* **Forms 3/4/5**: Holdings structure
   * Each entry represents a security holding
   * Flattened structure in CSV output
   * Nested structure preserved in JSON

* **Form D**: Related persons structure
   * Contains information about related persons
   * Flattened in CSV with related person details
   * Full structure preserved in JSON

* **NPORT-P**: Investment securities structure
   * Each entry represents an investment or security
   * Flattened for CSV output
   * Original structure maintained in JSON

Methods
-------

parse()
~~~~~~~
Parse the filing based on its type.

:Returns: Parsed filing data (dict)

write_json(output_filename=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Write data to JSON. Preserves nested structure where applicable.

:Parameters:
   ***output_filename** (*str, optional*) -- Output JSON filepath. Defaults to input filename with .json extension.

:Raises:
   **ValueError** -- If no data is available (parse() hasn't been called)

write_csv(output_filename=None, accession_number=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Write data to CSV. Flattens nested documents or writes tabular data directly.

:Parameters:
   ***output_filename** (*str, optional*) -- Output CSV filepath. Defaults to input filename with .csv extension.
   ***accession_number** (*str, optional*) -- SEC accession number to include in output

:Returns:
   **str** -- Path to created CSV file

:Raises:
   **ValueError** -- If no data is available (parse() hasn't been called)

Examples
--------

.. code-block:: python

   # Parse and write a 10-K filing
   doc = Document("10k_filing.txt", "10-K")
   doc.parse()
   doc.write_csv("output.csv")

.. code-block:: python

   # Process multiple Form 4 filings
   from pathlib import Path
   import pandas as pd
   
   dfs = []
   for file in Path('form4_files').iterdir():
       doc = Document(str(file), '4')
       doc.parse()
       for holding in doc:
           dfs.append(holding)
   
   df = pd.DataFrame(dfs)
   df.to_csv('form4_holdings.csv', index=False)

Notes
-----
* Document-type filings (10-K/10-Q/8-K/SC 13D/SC 13G) create section/text columns in CSV
* Information table (13F-HR-INFORMATIONTABLE) preserves original columns
* Forms 3/4/5 flatten holdings information in CSV
* Form D flattens related persons information
* NPORT-P flattens investment securities data
* Optional accession number added as extra column in CSV output
* When opening CSV files in Excel, use From Text/CSV option for correct column separation
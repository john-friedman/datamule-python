Filing
======

Parse and write SEC filings (8-K, 10-Q, 10-K, 13F-HR-INFORMATIONTABLE) to JSON or CSV formats.

.. code-block:: python

   Filing(filepath, filing_type)

:Parameters:
   * **filepath** (*str*) -- Path to the filing file
   * **filing_type** (*str*) -- Filing type ('8-K', '10-Q', '10-K', '13F-HR-INFORMATIONTABLE')

Note that a filing's tabular data can be accessed directly.

.. code-block:: python

   from datamule import Filing
   import pandas as pd
   
   pd.DataFrame(filing)


Data Structure
-------------
* **10-K/10-Q/8-K**: Nested document structure
   * Contains hierarchical sections (document -> item1 -> subitem1a, etc.)
   * CSV output flattens hierarchy with section paths (e.g., "document_item1_subitem1a")
   * Text content preserved in nested format for JSON output

* **13F-HR-INFORMATIONTABLE**: Tabular structure
   * Each row represents a holding
   * Direct mapping to CSV columns
   * No nested flattening required

Methods
-------

parse_filing()
~~~~~~~~~~~~~
Parse the filing based on its type (nested or tabular).

:Returns: Parsed filing data (dict)

write_json(output_filename=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Write data to JSON. Preserves nested structure for 10-K/10-Q/8-K filings.

write_csv(output_filename=None, accession_number=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Write data to CSV. Flattens nested documents or writes tabular data directly. If opening in Excel make sure to use From Text/CSV option otherwise the columns will not be separated correctly.

Examples
-------

.. code-block:: python

   from datamule import Downloader, Filing
   from pathlib import Path
   import pandas as pd
   downloader = Downloader()
   downloader.download(form='4',output_dir='4',date=('2021-01-07','2021-01-07'))
   dfs = []
   for file in Path('4').iterdir():
      filing = Filing(str(file), '4')
      dfs.append(pd.DataFrame(filing))

   df = pd.concat(dfs)
   df.to_csv('4.csv', index=False)

.. code-block:: python

   filing = Filing("myfile.txt", "13F-HR-INFORMATIONTABLE")
   filing.parse_filing()
   filing.write_csv("output.csv")

Notes
-----
* Document filings (10-K/10-Q/8-K) create section/text columns in CSV
* Information table (13F-HR-INFORMATIONTABLE) preserves original columns
* Optional accession number added as extra column in CSV output
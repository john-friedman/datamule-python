Parsing
=======

Currently parses documents with:
* .xml extension
* .txt extension if 10-K, 10-Q, 8-K, SC 13D, SC 13G
* .htm/.html extension if 10-K, 10-Q, 8-K, SC 13D, SC 13G 

Note: The parser will soon be updated to parse almost every document type.

Future
------
* parses all .htm/.html files
* parses most .pdf files (some are image-based and cannot be parsed)

Standardization
---------------

Parsing utilizes `doc2dict <https://github.com/john-friedman/doc2dict>`_ to convert documents to a dictionary format. Documents can be further standardized using the `mapping_dicts <https://github.com/john-friedman/datamule-python/tree/experimental/datamule/datamule/mapping_dicts>`_. Contributions to mapping dicts are highly appreciated!


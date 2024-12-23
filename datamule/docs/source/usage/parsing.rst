Parsing
=======

Basic Parsing
-------------

Currently parses Forms 3, 13F-HR, NPORT-P, SC 13D, SC 13G, 10-Q, 10-K, 8-K, and D using a basic parser. 

Note: The parser will soon be updated to parse almost every document type.

SGML Parsing
------------

SEC submissions are submitted in `SGML format <https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/0000950170-22-000796.txt>`_. Submissions contain both the metadata and multiple documents. Since the SEC has strict rate limits, downloading the original submission and extracting the documents is much faster than downloading the documents individually. 

.. code-block:: python

    from datamule import parse_sgml_submission

    parse_sgml_submission(file_path, output_dir)

.. note::

    I rewrote the SGML parser in Cython to be faster. I am new to Cython, so while the code works and is faster, I likely have made some obvious mistakes. Feel free to submit a PR if you see something that can be improved. `GitHub <https://github.com/john-friedman/datamule-python>`_ 
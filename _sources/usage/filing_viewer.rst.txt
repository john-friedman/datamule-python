Filing Viewer
============

The Filing Viewer module converts parsed filing JSON into interactive HTML with features like a table of contents sidebar.

Basic Usage
----------

.. code-block:: python

    from datamule import parse_textual_filing
    from datamule.filing_viewer import create_interactive_filing

    data = parse_textual_filing(
        url='https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm',
        return_type='json'
    )
    create_interactive_filing(data)

You can try out the Filings Viewer online at `datamule.xyz/filings_viewer <https://datamule.xyz/filings_viewer>`_.
Parsing
=======

SEC XBRL Parsing
--------------

Parse XBRL data in JSON format to tables:

.. code-block:: python

    from datamule import parse_company_concepts
    table_dict_list = parse_company_concepts(company_concepts)

Textual Filing Parsing
--------------------

Parse textual filings into different formats:

.. code-block:: python

    # Simplified HTML
    simplified_html = dm.parse_textual_filing(
        url='https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm', 
        return_type='simplify'
    )

    # Interactive HTML
    interactive_html = dm.parse_textual_filing(
        url='https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm', 
        return_type='interactive'
    )

    # JSON
    json_data = dm.parse_textual_filing(
        url='https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm', 
        return_type='json'
    )
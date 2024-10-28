Parsing
=======

SEC XBRL Parsing
--------------

Parse XBRL data in JSON format to tables:

.. code-block:: python

    from datamule import parse_company_concepts
    table_dict_list = parse_company_concepts(company_concepts)

Filing Parser
-----------

Currently parses 10-Ks, 10-Qs, 8-Ks, 13-F Information Tables using a basic parser. For a more advanced parser see the Textual Filing Parsing below.


.. code-block:: python

    from datamule import Filing
    
    # Initialize Filing object
    filing = Filing(path, filing_type='8-K')
    filing = Filing(path,filing_type='13F-HR-INFORMATIONTABLE')
    
    # Parse the filing, using the declared filing type
    parsed_data = filing.parse_filing()

Example 8-K output:

.. code-block:: json

    {
      "000000428504000011_form8k": {
        "content": {
          "ITEM 5.02": {
            "title": "ITEM 5.02",
            "text": "DEPARTURE OF DIRECTORS OR PRINCIPAL OFFICERS; ELECTION OF DIRECTORS; APPOINTMENT OF PRINCIPAL OFFICERS. d) Alcan Inc. announces that Dr. Onno H. Ruding was appointed Director of the Board on September 23, 2004. Dr. Ruding is a former Minister of Finance of the Netherlands and was an Executive Director of the International Monetary Fund in Washington, D.C. and a member of the Board of Managing Directors of AMRO Bank in Amsterdam. He is the former Vice Chairman of Citicorp and Citibank, N.A. Dr. Ruding serves as a director on the boards of Corning Inc., Holcim AG and RTL Group and is president of the Centre for European Policy Studies (CEPS) in Brussels. Dr. Ruding is also a member of the international advisory committees of Robeco Group and the Federal Reserve Bank of New York. Dr. Ruding has also been appointed as a member of the Human Resources and Corporate Governance Committees. -2-"
          },
          "SIGNATURES": {
            "title": "SIGNATURES",
            "text": "Pursuant to the requirements of the Securities Exchange Act of 1934, the registrant has duly caused this report to be signed on its behalf by the undersigned hereunto duly authorized. ALCAN INC. BY: /s/ Roy Millington Roy Millington Corporate Secretary Date: September 28, 2004 -3-"
          }
        }
      }
    }

Textual Filing Parsing
--------------------

Parse textual filings into different formats using the datamule api. Note: datamule api is in beta, so if you want to use this at scale, please reach out to me: `John G Friedman <https://www.linkedin.com/in/johngfriedman/>`_. 

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

Simplified HTML:

.. image:: ../_static/simplify.png
   :alt: Simplified HTML Output Example
   :align: center

Interactive HTML:

.. image:: ../_static/interactive.png
   :alt: Interactive HTML Output Example
   :align: center

JSON:

.. image:: ../_static/json.png
   :alt: JSON Output Example
   :align: center
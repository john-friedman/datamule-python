Known Issues
===========

SEC File Malformation
-------------------

Some SEC files are malformed, which can cause parsing errors. For example, this `Tesla Form D HTML from 2009 <https://www.sec.gov/Archives/edgar/data/1318605/000131860509000004/xslFormDX01/primary_doc.xml>`_ is missing a closing ``</meta>`` tag.

Workaround:

.. code-block:: python

    from lxml import etree

    with open('filings/000131860509000005primary_doc.xml', 'r', encoding='utf-8') as file:
        html = etree.parse(file, etree.HTMLParser())

Current Development Issues
------------------------

* Documentation needed for filing and parser modules
* Need to add current names to former names
* Conductor needs more robustness with new options
* Need to add facet filters for forms
* SEC search engine implementation pending
* MuleBot custom HTML templates needed
* MuleBot summarization features and token usage protections needed
* Path compatibility needs verification on non-Windows devices
* Analytics implementation pending
* Download success message accuracy needs improvement
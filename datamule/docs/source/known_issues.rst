Known Issues
=============

SEC File Malformation
----------------------
Some SEC files are malformed, which can cause parsing errors. For example, this Tesla Form D HTML from 2009 is missing a closing `</meta>` tag.

**Workaround:**

You can use the following Python code to work around this issue using the `lxml` library:

```python
from lxml import etree

with open('filings/000131860509000005primary_doc.xml', 'r', encoding='utf-8') as file:
    html = etree.parse(file, etree.HTMLParser())

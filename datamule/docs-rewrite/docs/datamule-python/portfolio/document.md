# Document

The `Document` class represents a single file in a SEC Submission.

## Attributes

* `document.accession` - submission accession number
* `document.path` - document file path
* `document.filing_date` - submission filing date
* `document.extension` - document file extension, e.g. '.xml'
* `document.content` - document in either string or bytes format.
* `document.data` - parsed document content created after `document.parse()`

##  `contains_string`
```python
contains_string(self, pattern)
```

### Example
```python
pattern = r'(?i)chatgpt'
document.contains_string(pattern)
```

## `parse`

Parses a document into dictionary form, and applies a mapping dict. Currently supports any file in `html`, `xml`, has limited support for `.pdf`, and some `txt` formats. Most do not have mapping dicts written yet, so are a bit less standardized.

## `parse_xbrl`

Parses the inline XBRL of a html document. Feature requests welcome.

[Example](https://github.com/john-friedman/datamule-python/blob/main/examples/parse_xbrl.ipynb)

## `parse_fundamentals`

```
parse_fundamentals(categories=None) # optional, e.g. ['balanceSheet']
```
[Example](https://github.com/john-friedman/datamule-python/blob/main/examples/fundamentals.ipynb)


## `visualize`

Opens a document using webbrowser. Only works for certain file extensions.

## `get_section`

Gets section by title.
```python
# returns a list of dictionaries preserving hierarcy - a list in case there are multiple sections with the same title
get_section(title='parti', format='dict'):
# returns a list of flattened version of dict form
get_section(title='signatures', format='text'):

# return all sections with title including item1, e.g. item1, item1a,...
get_section(r"item1.*",format='dict')

# returns all sections starting with income
get_section(r"income.*",format='dict')
```

Note that `get_section` will return matches for `title` (original title) or `standardized_title` (standarized title - e.g. "ITEM 1A. RISK FACTORS" -> 'item1a').




## `tables`
```python
document.tables()
```

If the document has extension '.xml', parses the xml into tables.

## `write_csv`
```python
write_csv(self, output_folder)
```
If the document has extension '.xml', parses the xml into tables, then writes to disk using append.

## `write_json`

Writes `self.data` to json.



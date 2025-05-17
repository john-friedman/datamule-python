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

Parses a document into dictionary form, and applies a mapping dict. Currently supports all XML files as well as:
`10-K`, `10-Q`, `8-K`, `SC 13D`, and `SC 13G`.

## `visualize`

Opens a document using webbrowser. Only works for certain file extensions.

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



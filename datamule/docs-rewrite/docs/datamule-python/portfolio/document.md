# Document

The `Document` class represents a single file in a SEC Submission.

## Attributes

* `document.accession` - submission accession number
* `document.path` - document file path
* `document.filing_date` - submission filing date
* `document.extension` - document file extension, e.g. '.xml'
* `document.content` - document in either string or bytes format
* `document.data` - parsed document content (automatically parsed when first accessed)
* `document.text` - available for html or txt files. Returns the text without formatting such as tags. (automatically parsed when first accessed)
* `document.tables` - parsed tables from XML documents (automatically parsed when first accessed)

## Lazy Loading

The Document class uses lazy loading for both `data` and `tables` attributes. This means:

- `document.data` automatically calls `parse()` when first accessed
- `document.tables` automatically calls `parse_tables()` when first accessed  
- You don't need to manually call `parse()` before accessing document content
- Parsing only happens once - subsequent accesses return the cached result

### Example
```python
doc = Document(...)

# This automatically parses the document
content = doc.data

# This automatically parses tables (if XML) or returns empty list
tables = doc.tables

# No manual parsing needed
doc.visualize()  # Works automatically
sections = doc.get_section("item1")  # Works automatically
```

## Methods

### `contains_string`
```python
contains_string(self, pattern)
```

Checks if the document content contains a specified pattern. Works for HTML, XML, and TXT files.

#### Example
```python
pattern = r'(?i)chatgpt'
document.contains_string(pattern)
```

### `parse`

Parses a document into dictionary form and applies a mapping dict. Currently supports files in `html`, `xml`, has limited support for `.pdf`, and some `txt` formats. Most do not have mapping dicts written yet, so are less standardized.

**Note:** You typically don't need to call `parse()` manually - accessing `document.data` will automatically trigger parsing if needed.

### `visualize`

Opens the parser version of a document using webbrowser. Only works for certain file extensions.

### `open`

Opens the document using webbrowser.

### `get_section`

Gets section by title.

```
get_section(title=None, title_regex=None,title_class=None, format='dict'):
```

```python
# returns a list of dictionaries preserving hierarchy - a list in case there are multiple sections with the same title
get_section(title='parti', format='dict')

# returns a list of flattened version of dict form
get_section(title='signatures', format='text')

# return all sections with title including item1, e.g. item1, item1a,... title_class restricts to nodes where class is 'item'
get_section(title_regex= r"item1.*", format='dict',title_class='item')

# returns all sections starting with income
get_section(title_regex= r"income.*", format='dict')
```

Note that `get_section` will return matches for `title` (original title) or `standardized_title` (standardized title - e.g. "ITEM 1A. RISK FACTORS" -> 'item1a').

### `tables`

```python
document.tables
```

If the document has extension '.xml', automatically parses the XML into tables when first accessed. For non-XML documents, returns an empty list.

### `write_csv`

```python
write_csv(self, output_folder)
```

If the document has extension '.xml', parses the XML into tables, then writes to disk using append mode.

### `write_json`

```python
write_json(self, output_filename)
```

Writes `document.data` to JSON format (automatically parses document if not already parsed).

## Deprecated Methods

### `parse_xbrl`

Functionality moved to the [Submission Class](submission.md#parse_xbrl)

### `parse_fundamentals`

Functionality moved to the [Submission Class](submission.md#parse_xbrl)
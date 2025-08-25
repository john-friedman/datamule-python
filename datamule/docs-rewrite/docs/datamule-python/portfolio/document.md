# Document

The `Document` class represents a single file in a SEC Submission.

## Attributes

### Metadata
* `document.accession` - submission accession number
* `document.path` - document file path
* `document.filing_date` - submission filing date
* `document.extension` - document file extension, e.g. '.xml'

### `document.content`
Document in either string or bytes format.

### `document.data`
Document content parsed into dictionary form. 

### `document.text`
Available for html or text files. Returns the document's text.

### `document.tables`
Tabular data extracted from XML documents.

### `tags`

Tags extracted from documents. For example: cusips, persons, etc. Only works for html or text files currently.

Tags are an experimental feature to add "good enough" NLP to the SEC corpus, without compromising speed or bloating the package. How tags work is that they leverage basic pattern matching (fast + lightweight) alongside dictionary lookup of pre-computed NLP datasets.

It is highly recommended to use a [pre computed dataset](#dictionaries) to improve quality. Or don't, if you want to see how bad older forms of NLP can be.

Usage
```
document.text.tags.cusip # Get cusips from text in form (match,start position, end position)
document.data.tags.cusip # Get cusips from data in form (match, id of text or title segment, start position, end position)
```

Example
```
from datamule import Portfolio
from time import time
from datamule.tags.config import set_dictionaries

set_dictionaries(['13fhr_information_table_cusips'])

portfolio = Portfolio('13fhr')
portfolio.download_submissions(submission_type=['13F-HR'],filing_date=('2008-09-01','2008-09-30'))

for sub in portfolio:
    for doc in sub:
        results = doc.text.tags.cusips
        if results is not None:
            print(results)
```


#### Supported Tags:

- cusips
- isins
- figis
- persons
- tickers
    - nyse
    - nasdaq
    - nyse_american
    - london_stock_exchange
    - toronto_stock_exchange
    - euronext_paris
    - euronext_amsterdam
    - euronext_brussels
    - euronext_lisbon
    - euronext_milan
    - deutsche_borse_xetra
    - six_swiss_exchange
    - tokyo_stock_exchange
    - hong_kong_stock_exchange
    - shanghai_stock_exchange
    - shenzhen_stock_exchange
    - australian_securities_exchange
    - singapore_exchange
    - nse_bse
    - sao_paulo_b3
    - mexico_bmv
    - korea_exchange
    - taiwan_stock_exchange
    - johannesburg_stock_exchange
    - tel_aviv_stock_exchange
    - moscow_exchange
    - istanbul_stock_exchange
    - nasdaq_stockholm
    - oslo_bors
    - otc_markets_us
    - pink_sheets

### `similarity`

Usage
```
document.text.similarity.loughran_mcdonald 
document.data.similarity.loughran_mcdonald # get similarity by section
```

### Dictionaries
To improve tag quality, use a dictionary. On first load, these dictionaries are downloaded into the User's home. e.g. for Windows: `C:\Users\{username}\.datamule\dictionaries`.

```python
from datamule.tags.config import set_dictionaries
set_dictionaries(['ssa_baby_names'], overwrite=False) # set this to true, to download the latest dataset.
```

#### Tags
Persons

- ssa_baby_names (Uses all baby first names since 1880, where there are more than 5 names per year.)
- 8k_2024_persons (Uses multistage spacy, human parser pipeline to extract names from all documents within 2024 8-K filings)

CUSIP

- sc13dg_cusips (Uses SC 13D/G, somewhat incomplete)
- 13fhr_information_table_cusips.txt (Uses 13F-HR INFORMATION TABLE, should be better)

ISIN

- npx_isins (Uses isins detected in N-PX filings, very incomplete)

FIGI

- npx_figis (Uses figis detected in N-PX filings, very incomplete)


#### Similarity

Loughran McDonald

- loughran_mcdonald ([Link](https://sraf.nd.edu/loughranmcdonald-master-dictionary/))

## Methods

### `contains_string`
```python
contains_string(self, pattern)
```

Checks if the document content contains a specified pattern. Works for HTML, XML, and TXT files.

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

### `visualize`

Opens the parser version of a document using webbrowser. Only works for certain file extensions.

### `open`

Opens the document using webbrowser.

Example
```python
pattern = r'(?i)chatgpt'
document.contains_string(pattern)
```

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

## Legacy Methods
### `parse`

Parses a document into dictionary form and applies a mapping dict. Currently supports files in `html`, `xml`, has limited support for `.pdf`, and some `txt` formats. Most do not have mapping dicts written yet, so are less standardized.

Note: You typically don't need to call `parse()` manually - accessing `document.data` will automatically trigger parsing if needed.

## Architecture

### Lazy Loading
The Document class uses lazy loading.

# Index

Index is a class that allows you to search SEC submissions using simple or complex search terms.

## Methods

### `search_submissions`

```python
search_submissions(
        self,
        text_query,
        filing_date=None,
        submission_type=None,
        cik=None,
        ticker=None,
        requests_per_second=5.0,
        quiet=True,
        **kwargs
    ):
```

### Results Format

The `search_submissions` method returns a list of dictionaries containing search results:

```
[
{
    "_index": "edgar_file",
    "_id": "0001628280-24-002390:tsla-2023x12x31xex211.htm",
    "_score": 10.79173,
    "_source": {
        "ciks": ["0001318605"],
        "period_ending": "2023-12-31",
        "file_num": ["001-34756"],
        "display_names": ["Tesla, Inc.  (TSLA)  (CIK 0001318605)"],
        "root_forms": ["10-K"],
        "file_date": "2024-01-29",
        "form": "10-K",
        "adsh": "0001628280-24-002390",
        "file_type": "EX-21.1",
        "file_description": "EX-21.1",
        # Additional fields omitted for brevity
    }
},...
]
```

### Parameters

- **text_query**: Text to search for in SEC filings
- **filing_date**: Filing date in form `('YYYY-MM-DD','YYYY-MM-DD')`
- **submission_type**: Type of SEC submission (e.g., '10-K', '10-Q', '8-K')
- **cik**: CIK(s) to filter by (company identifier(s))
- **ticker**: Ticker(s) to filter by (stock symbol(s))
- **quiet**: Whether to suppress output (default: True)

### Text Query Syntax

The `text_query` parameter supports a modified Elasticsearch syntax with the following operators:

#### 1. Boolean Operators
- `term1 OR term2` - Either term can appear
- `term1 NOT term2` or `term1 -term2` - Excludes documents containing the second term
- `term1 term2` - Both terms must appear.
- Example: `revenue OR growth NOT decline`

#### 2. Exact Phrase Matching
- Use double quotes for exact phrase matching
- Example: `"revenue growth"`

#### 3. Wildcards
- Single character (`?`) and multiple character (`*`) wildcards
- Example: `risk factor?` - Matches "risk factor", "risk factors", etc.

#### 4. Boosting
- Use double asterisk (`**`) followed by a number to increase term importance
- Example: `revenue**2 growth` - Makes "revenue" twice as important

### Limitations to Note

- **Complex Nesting**: Avoid using parentheses for grouping as they may be interpreted as literal search terms
  - Instead of: `(revenue OR sales) AND growth`
  - Use: `"revenue growth" OR "sales growth"`

- **Proximity & Fuzzy Searches**: This implementation does not support proximity searches with the tilde operator (`~`) or fuzzy matching

### **kwargs

For additional search parameters see [metadata filtering](../utils/_process_cik_and_metadata_filters.md).


### Key Components of Results
- `_id`: Document identifier (format: accession_number:matched document)
- `_score`: Relevance score indicating match quality
- `_source`: Filing metadata including:
  - `ciks`: Company identifiers
  - `period_ending`: End date of reporting period
  - `display_names`: Company name with ticker and CIK
  - `root_forms`: Primary form type
  - `file_date`: Filing date
  - `adsh`: Accession number

## Examples

```python
# Search for "risk factors" in Apple's 10-K filings
index = Index()
results = index.search_submissions(
    text_query='"risk factors"',
    submission_type="10-K",
    ticker="AAPL",
    start_date="2020-01-01",
    end_date="2023-12-31"
)

# Search for "war" but exclude "peace" in 10-K filings from January 2023
results = index.search_submissions(
    text_query='war NOT peace',
    submission_type="10-K",
    start_date="2023-01-01",
    end_date="2023-01-31",
    quiet=False,
    requests_per_second=3
)
```
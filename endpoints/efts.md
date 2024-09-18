# Edgar Full Text Search

Links: [Edgar Full Text Search](https://www.sec.gov/edgar/search/), [Endpoint](https://efts.sec.gov/LATEST/search-index?q=the)


## Response
- `took`: The time in milliseconds that Elasticsearch took to execute the query.
- `timed_out`: Indicates whether the query timed out (false in this case, meaning it completed successfully).
- `_shards`: Information about the index shards that were searched:
  - `total`: Total number of shards that were queried.
  - `successful`: Number of shards that successfully executed the query.
  - `skipped`: Number of shards that were skipped.
  - `failed`: Number of shards that failed during the query execution.
- `hits`: Contains the search results and metadata:
  - `total`: 
    - `value`: The total number of documents that matched the query.
    - `relation`: Indicates how the total count relates to the actual number of matching documents.
  - `max_score`: The maximum relevance score among the matching documents.
  - `hits`: An array of the matching documents, each containing:
    - `_index`: The name of the Elasticsearch index containing the document.
    - `_type`: The document type (deprecated in newer Elasticsearch versions).
    - `_id`: A unique identifier for the document within the index.
    - `_score`: The relevance score of this document for the given query.
    - `_source`: The original JSON document that was indexed, containing:
      - `ciks`: Central Index Key(s) identifying the company in SEC filings.
      - `period_ending`: The end date of the reporting period for the filing.
      - `root_form`: The primary SEC form type (e.g., 8-K, 10-K).
      - `file_num`: SEC file number(s) associated with the company.
      - `display_names`: Company name(s) and associated ticker symbol.
      - `xsl`: XSL stylesheet information (null in this case).
      - `sequence`: The sequence number of this document within the filing.
      - `file_date`: The date the document was filed with the SEC.
      - `biz_states`: State(s) where the company conducts business.
      - `sics`: Standard Industrial Classification code(s) for the company.
      - `form`: The specific SEC form type for this document.
      - `adsh`: SEC Accession Number, a unique identifier for the filing.
      - `film_num`: SEC Film Number(s) associated with the filing.
      - `biz_locations`: Primary business location(s) of the company.
      - `file_type`: The type of file within the SEC filing (e.g., EX-3.2 for Exhibit 3.2).
      - `file_description`: A description of the file type.
      - `inc_states`: State(s) of incorporation for the company.
      - `items`: Specific item numbers from the SEC form that are addressed in this filing.
- `aggregations`: Provides summarized data about the search results:
  - `entity_filter`: Groups results by company names:
    - `doc_count_error_upper_bound`: Estimate of the maximum number of entities that may be missing from the results.
    - `sum_other_doc_count`: Count of entities not included in the top results.
    - `buckets`: List of top entities, each with:
      - `key`: Company name and CIK (Central Index Key).
      - `doc_count`: Number of documents for this entity.
  - `sic_filter`: Groups results by Standard Industrial Classification (SIC) codes:
    - Similar structure to `entity_filter`, but for SIC codes.
  - `biz_states_filter`: Groups results by business states:
    - Similar structure, showing documents per state.
  - `form_filter`: Groups results by SEC form types:
    - Shows document count for each form type (e.g., 8-K, 10-Q, 10-K).
- `query`: The Elasticsearch query used to generate these results:
  - `bool`: A boolean query combining multiple conditions:
    - `must`: Conditions that must be met (e.g., documents containing "the").
    - `filter`: Additional filtering criteria:
      - `terms`: Includes specific document types (various SEC forms).
      - `range`: Limits results to a specific date range.
  - `from` and `size`: Control pagination of results.
  - `aggregations`: Defines the aggregations explained above.

## Parameters
https://efts.sec.gov/LATEST/search-index?q=the&dateRange=all&category=form-cat1&locationCode=CA&ciks=0000320193&entityName=Apple%20Inc.%20(AAPL)%20(CIK%200000320193)&forms=1-K%2C1-SA%2C1-U%2C1-Z%2C1-Z-W%2C10-D%2C10-K%2C10-KT%2C10-Q%2C10-QT%2C11-K%2C11-KT%2C13F-HR%2C13F-NT%2C15-12B%2C15-12G%2C15-15D%2C15F-12B%2C15F-12G%2C15F-15D%2C18-K%2C20-F%2C24F-2NT%2C25%2C25-NSE%2C40-17F2%2C40-17G%2C40-F%2C6-K%2C8-K%2C8-K12G3%2C8-K15D5%2CABS-15G%2CABS-EE%2CANNLRPT%2CDSTRBRPT%2CIRANNOTICE%2CN-30B-2%2CN-30D%2CN-CEN%2CN-CSR%2CN-CSRS%2CN-MFP%2CN-MFP1%2CN-MFP2%2CN-PX%2CN-Q%2CNPORT-EX%2CNSAR-A%2CNSAR-B%2CNSAR-U%2CNT%2010-D%2CNT%2010-K%2CNT%2010-Q%2CNT%2011-K%2CNT%2020-F%2CQRTLYRPT%2CSD%2CSP%2015D2&locationCodes=CA&startdt=2001-01-01&enddt=2024-09-17

`q`: searches to see if text is in the document. E.g. 'iPad'.
`dateRange`: I don't think this does anything.
`category`: I don't think this does anything.
`locationCode`:
`locationCodes`:
`ciks`: 
`entityName`: 
`forms`: We use this. It grabs amended forms as well, e.g. 10K and 10K/A
`startdt`: We use this.
`enddt`: We use this.
`filter_forms`: 


Note: sec.gov has a 10r/s rate limit
I think efts has a seperate rate limit
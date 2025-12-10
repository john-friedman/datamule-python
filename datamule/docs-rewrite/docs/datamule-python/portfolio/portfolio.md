# Portfolio

The `Portfolio` class lets you interact with SEC Submissions. Portfolio's consist of a folder that contains subfolders named after SEC Submission accession numbers.

## Attributes
* `portfolio.path` - path to folder

## `set_api_key`

Use this if you don't want to store the api key as environmental variable.
```python
set_api_key(api_key)
```

## `download_submissions`

There are three providers to download from:
- `sec`, which has a rate limit of 5/s over long durations, 10/s over short durations.
- `datamule-sgml`, which has no rate limit and depends on your internet speed/cpu. Users have reported getting 1gbps while running in the Cloud. See [How to host the SEC archive for $20/month](https://medium.com/@jgfriedman99/how-to-host-the-sec-archive-for-20-month-da374cc3c3fb).
- `datamule-tar`, which is like `datamule` but much faster when you only need some documents within a submission. New, may have bugs. See [Programmatically downloading SEC attachments in bulk](https://medium.com/@jgfriedman99/programmatically-downloading-sec-attachments-in-bulk-a072489002fb).

`datamule-sgml` and `datamule-tar` also have more args to filter on. This is because they datamule's internal databases instead of the SEC.

Note that: `datamule` -> `datamule-sgml`.

### `provider='sec'`
```python
download_submissions(self, cik=None, ticker=None, submission_type=None, filing_date=None, provider=None,document_type=None,keep_filtered_metadata=False, requests_per_second=5,skip_existing=True, **kwargs)
```

### Example
Download every IBM 10-K between 2019 and 2024
```
portfolio = Portfolio('ibm')
portfolio.download_submissions(filing_date=('2019-01-01', '2024-01-01'), submission_type='10-K',
                          provider='sec')
```


### Parameters
* cik - company CIK, e.g. `0001318605` or `1318605` or `['0001318605','789019']`
* ticker - e.g. `'TSLA'` or `['TSLA','AAPL','MSFT']`
* submission_type - the submission type e.g. `'10-K'` or `['3','4','5']`
* document_type - arg for downloading only a specific document type in a submission. e.g. setting to `'PROXY VOTING RECORD'` for `submission_type='N-PX'` will only download the proxy voting record file.
* filing_date - e.g. `'2023-05-09'` or `('2023-01-01','2024-01-01')` or `['2023-01-01','2024-21-11','2025-23-01']
* provider - e.g. `sec` or `datamule`. will use defaults from [config](../data_provider.md)
* requests_per_second - sec hard rate limit is 10/s, soft limit is 5/s over long durations.
* keep_filtered_metadata - whether metadata on documents within a submission should be kept or discarded if documents are filtered.
* skip_existing - whether to download submissions already in the Portfolio.
* [**kwargs](../utils/_process_cik_and_metadata_filters.md)

## `provider='datamule'`
```python
download_submissions(self, cik=None, ticker=None, submission_type=None, filing_date=None, provider=None, document_type=[],
                         keep_filtered_metadata=False, standardize_metadata=True, skip_existing=True,
                         accession_numbers=None, report_date=None, detected_time=None, contains_xbrl=None, sequence=None,
                         quiet=False, filename=None, **kwargs)
```

### Example

Only download the graphics from Apple's submissions.
```
portfolio = Portfolio('apple_graphics')
portfolio.download_submissions(ticker='AAPL',document_type="GRAPHIC",
                          provider='datamule-tar')
```

Download every IBM Form 4 since 1994.
```
portfolio = Portfolio('ibm')
portfolio.download_submissions(submission_type=['4','4/A'],
                          provider='datamule-sgml')
```

### Additional Parameters
* report_date - Report period of the Submission.
* contains_xbrl - Whether the Submission contains XBRL.
* sequence - order of documents within a Submission.
* filename - filename of a document within the Submission.

### Filtering

Filtering filters what submissions are downloaded. Filters can be chained.

#### Example
```python
portfolio.filter_text('"climate change"', filing_date=('2019-01-01', '2019-01-31'), submission_type='10-K')
portfolio.filter_text('drought', filing_date=('2019-01-01', '2019-01-31'), submission_type='10-K')
portfolio.download_submissions(filing_date=('2019-01-01', '2019-01-31'), submission_type='10-K')
```


#### `filter_text`
```python
filter_text(self, text_query, cik=None, ticker=None, submission_type=None, filing_date=None, **kwargs)
```
##### Parameters
* text_query - e.g. "machine learning". For more information click [here](../index/index.md)
* cik - company CIK, e.g. `0001318605` or `1318605` or `['0001318605','789019']`
* ticker - e.g. `'TSLA'` or `['TSLA','AAPL','MSFT']`
* submission_type - the submission type e.g. `'10-K'` or `['3','4','5']`
* filing_date - e.g. `'2023-05-09'` or `('2023-01-01','2024-01-01')` or `['2023-01-01','2024-21-11','2025-23-01']
* [**kwargs](../utils/_process_cik_and_metadata_filters.md)

#### `filter_xbrl`
```python
filter_xbrl(self, taxonomy, concept, unit, period, logic, value)
```

For help filling out args, see [this](https://www.sec.gov/search-filings/edgar-application-programming-interfaces#:~:text=data.sec.gov/api/xbrl/frames/).

##### Parameters
* taxonomy - e.g. `dei`,`us-gaap`, etc.
* concept - e.g. `AccountsPayableCurrent`
* unit - e.g. `USD`
* period - e.g. `CY2019Q4I`
* logic - `'>'`,`'>='`,`'=='`,`'!='`, `'<='`, `'<'`

## `monitor_submissions`
Monitor the SEC for new submissions.
```python
monitor_submissions(data_callback=None, interval_callback=None,
                            polling_interval=1000, quiet=True, start_date=None,
                            validation_interval=60000)
```
### hits format:
```python
[{'accession': 176693425000001, 'submission_type': 'D/A', 'ciks': ['1766934'], 'filing_date': '2025-05-28'}...]
```
### Parameters
* data_callback - function that uses hits
* interval_callback - function that is called between polls
* quiet - whether to print output
* start_date - start date for backfill
* polling_interval - time in ms to poll the rss feed. If set to None, will never poll
* validation_interval - time to run more robust check of what submissions have been submitted. If set to None, will never validate

???+ note "rate limit sharing"
    will update this later to add documentation for rate limit sharing - e.g. downloading each submission as they come out

### Example
```python
from datamule import Portfolio
from time import time

start_time = time()

portfolio = Portfolio('test')
portfolio.monitor.set_domain_rate_limit(domain='sec.gov', rate=3)
def interval_callback():
    global start_time
    print(f"elapsed time: {time() - start_time} seconds")

def data_callback(hits):
    print(f"Number of new hits: {len(hits)}")

portfolio.monitor_submissions(validation_interval=60000,start_date='2025-04-25',
                                   quiet=True,polling_interval=1000,
                                   interval_callback=interval_callback,data_callback=data_callback)
```

??? note "Architecture"
    There are two ways to Monitor SEC submissions in real time.
    1. RSS - ~25% of submissions are missed
    2. EFTS - often 30-50s slower than the RSS feed
    The `Monitor` class is a compromise that uses both systems. I will likely do a write up on how it works later on, because both systems are annoying to work with. If you have a use-case that requires insane levels of speed, feel free to email me for advice.


## `stream_submissions`
Get new SEC submissions by listening to datamule's websocket. Requires an [API Key](https://datamule.xyz/dashboard2). 
```python
stream_submissions(data_callback=None,api_key=None,quiet=False)
```

### hits format:
```python
[{'accession': '95017025085535', 'submission_type': '4', 'ciks': ['109198', '1278731'], 'filing_date': '2025-06-12', 'detected_time': 1749762028168, 'source': 'rss'}...]
```

### Parameters
* data_callback - function that uses hits
* quiet - whether to print output

### Example
```
portfolio = Portfolio('websockettest')

def data_callback(hits):
    for hit in hits:
        print(hit)
portfolio.stream_submissions(data_callback=data_callback)
```




## `document_type`

Iterate through documents in a portfolio based on type.

### Example
```python
for document in portfolio.document_type('10-K'):
    print(document.path)
```

## Iterable

Iterate through submissions in a portfolio.

### Example
```python
for submission in portfolio:
    print(submission.path)
```

## `process_submissions`

Process submissions within a portfolio using threading (faster).
```python
process_submissions(self, callback)
```

## `decompress`
Decompress all batch tar files back to individual submission directories.
```python
decompress(self, max_workers=None)
```

### Parameters
* max_workers - Number of threads for parallel file processing (default: portfolio.MAX_WORKERS)

### Example
```python
# Extract all batch tar files to individual submission directories
portfolio.decompress()

# Use custom number of worker threads
portfolio.decompress(max_workers=4)
```

???+ note "Complete Extraction"
    This method extracts all submissions from batch tar files back to individual `accession_number/` directories in the portfolio root. Batch tar files are removed after successful extraction.

### Example
```python
def callback_function(submission):
    print(submission.metadata['cik'])

# Process submissions - note that filters are applied here
portfolio.process_submissions(callback=callback_function)
```

## `process_documents`
Process documents within a portfolio using threading (faster).
```python
process_documents(self, callback)
```

### Example
```python
def callback_function(document):
    print(document.path)

# Process submissions - note that filters are applied here
portfolio.process_documents(callback=callback_function)
```

## `delete`
Deletes the portfolio's folder and reinitializes an empty Portfolio object.
```python
delete()
```

### Example
```python
from datamule import Portfolio
port = Portfolio('deletetest')
port.delete()
port.download_submissions(ticker='MSFT',submission_type='10-K')
port.delete()
port.download_submissions(ticker='MSFT',submission_type='10-K')
```
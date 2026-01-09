# Monitor New Filings

You can monitor new filings either by using the websocket (uses datamule's websocket, streams in real time), or by polling the SEC.

> If you are interested in getting filings the way HFT does, see [The fastest way to get SEC filings](https://github.com/john-friedman/The-fastest-way-to-get-SEC-filings).

## Websocket

Requires an [api key](https://datamule.xyz/dashboard). One connection per user, costs $0.001 each time user connects to websocket (resource control mechanism). 
```python
from datamule import Portfolio
from datamule.utils.convenience import construct_index_url, construct_sgml_url, construct_folder_url


portfolio = Portfolio('websocket')

def data_callback(hits):
    for hit in hits:
        print(f"Index url: {construct_index_url(hit['accession'])}")
        print(f"SGML url: {construct_sgml_url(hit['accession'],hit['ciks'][0])}")
        print(f"Folder url: {construct_folder_url(hit['accession'],hit['ciks'][0])}")

portfolio.stream_submissions(data_callback=data_callback,quiet=False)
```

Websocket is an EC2 go server, updated by two EC2 t4g.nano instances running the polling logic. One instance is dedicated to RSS, other to EFTS. Should update within 250ms.

## Polling

Polling by default hits both the RSS endpoint (fastest, but misses filings) and EFTS endpoint (slower, but complete).

> It is recommended to use datamule's method to poll EFTS rather than make your own. This is because EFTS has a max return size of 10,000. There may be more than 10,000 filings in a day, so getting every filing requires some tricks that datamule implements well.

```python
from datamule import Portfolio
from datamule.utils.convenience import construct_index_url, construct_sgml_url, construct_folder_url


portfolio = Portfolio('monitor')

def data_callback(hits):
    for hit in hits:
        print(f"Index url: {construct_index_url(hit['accession'])}")
        print(f"SGML url: {construct_sgml_url(hit['accession'],hit['ciks'][0])}")
        print(f"Folder url: {construct_folder_url(hit['accession'],hit['ciks'][0])}")

portfolio.monitor_submissions(data_callback=data_callback, interval_callback=None,
                            polling_interval=1000, quiet=True, start_date=None,
                            validation_interval=60000)
```
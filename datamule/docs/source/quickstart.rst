Quickstart
==========

downloader
----------

```python
from datamule import Downloader
downloader = Downloader()
downloader.download_filings(
    output_dir='ford8k',
    ticker='F',
    form=['8-K']
)


premium downloader
------------------

```python
from datamule import PremiumDownloader
downloader = PremiumDownloader()
downloader.download_filings(
    output_dir='ford8k',
    ticker='F',
    form=['8-K']
)

parsing
-------
from datamule import Submission
submission = Submission('ford8k/000003799621000010/')
for document in submission.document_type('8-K'):
    document.parse()
    print(document.data)
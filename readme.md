![PyPI - Downloads](https://img.shields.io/pypi/dm/datamule)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fjohn-friedman%2Fdatamule-python&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![GitHub](https://img.shields.io/github/stars/john-friedman/datamule-python)
## datamule

A python package to make using SEC filings easier. Currently makes downloads easier and faster. 

Links: [Download Indices](https://www.mediafire.com/folder/9szwq6k80t4de/sec_indices) (900mb)


Installation
```
pip install datamule
```

## Quickstart:

Either download the pre-built indices from the links in the readme and set the indices_path to the folder
```
from datamule import Downloader
downloader = Downloader()
downloader.set_indices_path(indices_path)
```

Or run the indexer
```
from datamule import Indexer
indexer = Indexer()
indexer.run()
```

Example Downloads
```
# Example 1: Download all 10-K filings for Tesla using CIK
downloader.download(form='10-K', cik='1318605', output_dir='filings')

# Example 2: Download 10-K filings for Tesla and META using CIK
downloader.download(form='10-K', cik=['1318605','1326801'], output_dir='filings')

# Example 3: Download 10-K filings for Tesla using ticker
downloader.download(form='10-K', ticker='TSLA', output_dir='filings')

# Example 4: Download 10-K filings for Tesla and META using ticker
downloader.download(form='10-K', ticker=['TSLA','META'], output_dir='filings')

# Example 5: Download every form 3 for a specific date
downloader.download(form ='3', date='2024-05-21', output_dir='filings')

# Example 6: Download every 10K for a year
downloader.download(form='10-K', date=('2024-01-01', '2024-12-31'), output_dir='filings')

# Example 7: Download every form 4 for a list of dates
downloader.download(form = '4',date=['2024-01-01', '2024-12-31'], output_dir='filings')
```

Future:
* Integration with datamule's SEC Router endpoint for downloading on the fly
* Integration with datamule's SEC Router bulk data endpoint to remove need for indexing.

Update Log:
9/7/24
* Simplified indices approach
* Switched from pandas to polar. Loading indices now takes under 500 milliseconds.
* reuploaded indices to mediafire - todo


![PyPI - Downloads](https://img.shields.io/pypi/dm/datamule)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fjohn-friedman%2Fdatamule-python&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![GitHub](https://img.shields.io/github/stars/john-friedman/datamule-python)
# datamule
A python package to make using SEC filings easier. Integrated with [datamule](https://datamule.xyz/)'s APIs and datasets.

## features
current:
* parse textual filings into simplified html, interactive html, or structured json.
* download sec filings quickly and easily
* download datasets such as every MD&A from 2024 or every 2024 10K converted to structured json


Installation
```
pip install datamule
```

## quickstart:

### parsing
Uses endpoint: https://jgfriedman99.pythonanywhere.com/parse_url with params url and return_type. Current endpoint can be slow. If it's too slow for your use-case, please contact me.

#### simplified html
```
simplified_html = dm.parse_textual_filing(url='https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm',return_type='simplify')
```
![Alt text](https://raw.githubusercontent.com/john-friedman/datamule-python/main/static/simplify.png "Optional title")
[Download Example](https://github.com/john-friedman/datamule-python/blob/main/static/appl_simplify.htm)


#### interactive html
```
interactive_html = dm.parse_textual_filing(url='https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm',return_type='interactive')
```


![Alt text](https://raw.githubusercontent.com/john-friedman/datamule-python/main/static/interactive.png "Optional title")
[Download Example](https://github.com/john-friedman/datamule-python/blob/main/static/appl_interactive.htm)

#### json
```
d = dm.parse_textual_filing(url='https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm',return_type='json')
```

![Alt text](https://raw.githubusercontent.com/john-friedman/datamule-python/main/static/json.png "Optional title")
[Download Example](https://github.com/john-friedman/datamule-python/blob/main/static/appl_json.json)


### downloading filings using the indices api 
Limited to 10,000 results per query. Uses endpoint: https://api.datamule.xyz/submissions. A full list of params can be found here (SEC Router)[https://medium.com/@jgfriedman99/sec-router-05a2308b24ce]

```
from datamule import Downloader
downloader = Downloader()
downloader.download_using_api(form='10-K',ticker='AAPL')
```

### downloading filings without the indices api

Either download the pre-built indices from the links in the readme and set the indices_path to the folder
```
from datamule import Downloader
downloader = Downloader()
downloader.set_indices_path(indices_path)
```

Or run the indexer. Downloading indices takes about 30 seconds, re-running takes about 20 minutes.
```
from datamule import Indexer
indexer = Indexer()
indexer.run(download=False)
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

### datasets

Need a better way to store datasets, as I'm running out of storage. Currently stored on [Dropbox](https://www.dropbox.com/scl/fo/byxiish8jmdtj4zitxfjn/AAaiwwuyaYp_zRfFyqfBUS8?rlkey=sx7g5uxrz4dn35c593584ztds&st=yohhlwfx&dl=0) 2gb free tier.
```
downloader.download_dataset('10K')
downloader.download_dataset('MDA')
```


## Update Log
9/14/24
* added support for parser API

9/13/24
* added download_datasets
* added option to download indices
* added support for jupyter notebooks

9/9/24
* added download_using_api(self, output_dir, **kwargs). No indices required.

9/8/24
* Added integration with datamule's SEC Router API

9/7/24
* Simplified indices approach
* Switched from pandas to polar. Loading indices now takes under 500 milliseconds.

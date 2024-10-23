# datamule

![PyPI - Downloads](https://img.shields.io/pypi/dm/datamule)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fjohn-friedman%2Fdatamule-python&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![GitHub](https://img.shields.io/github/stars/john-friedman/datamule-python)

A Python package to work with SEC filings at scale. Also includes [Mulebot](https://chat.datamule.xyz/), an open-source chatbot for SEC data that does not require storage. Integrated with [datamule](https://datamule.xyz/)'s APIs and datasets.

Articles:
[How to deploy a financial chatbot to the internet in 5 minutes](https://medium.com/@jgfriedman99/how-to-deploy-a-financial-chatbot-in-5-minutes-ef5eec973d4c)

## Features
- Monitor EDGAR for new filings
- Parse textual filings into simplified HTML, interactive HTML, or structured JSON
- Download SEC filings quickly and easily
- Access datasets such as every 10-K, SIC codes, etc.
- Download 100,000 MD&A since 2001. (beta, requires free api_key)
- Interact with SEC data using MuleBot

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Downloader](#downloader)
  - [Parsing](#parsing)
  - [Filing Viewer](#filing-viewer)
  - [MuleBot](#mulebot)
- [Examples](#examples)
- [Known Issues](#known-issues)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Change Log](#change-log)
- [Other Useful SEC Packages](#other-useful-sec-packages)

## Installation

Basic installation:
```bash
pip install datamule
```

Installation with additional features:
```bash
pip install datamule[filing_viewer]  # Install with filing viewer module
pip install datamule[mulebot]  # Install with MuleBot
pip install datamule[all]  # Install all extras
```

Available extras:
- `filing_viewer`: Includes dependencies for the filing viewer module
- `mulebot`: Includes MuleBot for interacting with SEC data
- `mulebot_server`: Includes Flask server for running MuleBot
- `all`: Installs all available extras

## Quick Start

```python
import datamule as dm

downloader = dm.Downloader()
downloader.download(form='10-K', ticker='AAPL')
```

### Package Data CSVs
- [company_former_names.csv](https://github.com/john-friedman/datamule-python/blob/main/datamule/datamule/data/company_former_names.csv) - former names of companies
- [company_metadata.csv](https://raw.githubusercontent.com/john-friedman/datamule-python/refs/heads/main/datamule/datamule/data/company_metadata.csv) - metadata including sic classification
- [company_tickers.csv](https://github.com/john-friedman/datamule-python/blob/main/datamule/datamule/data/company_tickers.csv) - cik, ticker, name
- [sec-glossary.csv](https://github.com/john-friedman/datamule-python/blob/main/datamule/datamule/data/sec-glossary.csv) - form and description
- [xbrl_descriptions.csv](https://github.com/john-friedman/datamule-python/blob/main/datamule/datamule/data/xbrl_descriptions.csv) - category fact description

#### Updating Package Data
```python
downloader.update_company_tickers()
downloader.update_metadata()
```

## API Key
Some datasets / features require an API key. 

[WIP]

## Usage

### Downloader

```python
downloader = dm.Downloader()
```

#### Downloading Filings

Uses the [EFTS API](https://efts.sec.gov/LATEST/search-index) to retrieve filings locations, and the [SEC API](sec.gov) to download filings.
```python
download(self, output_dir='filings', return_urls=False, cik=None, ticker=None, form=None, date=None, sics=None, items=None, file_types=None)
```

```python
# Download all 10-K filings for Tesla using CIK
downloader.download(form='10-K', cik='1318605', output_dir='filings')

# Download 10-K filings for multiple companies using tickers
downloader.download(form='10-K', ticker=['TSLA', 'META'], output_dir='filings')

# Download every form 3 for a specific date
downloader.download(form='3', date='2024-05-21', output_dir='filings')

# Download filing attachments such as information tables
downloader.download(form='13F-HR',file_types=['INFORMATION TABLE'],date=('2024-09-14','2024-09-16'))

# Download based on items
downloader.download(form='8-K',items=['8.01'])
```

View the SEC Filing Glossary [here](https://datamule.xyz/sec_glossary) or download the json file [here](https://datamule.xyz/static/sec-glossary.json).

#### Downloading Company Concepts XBRL

Uses the [Company Concepts API](https://data.sec.gov/api/xbrl/companyfacts/CIK0001318605.json) to retrieve XBRL.

```python
download_company_concepts(self, output_dir = 'company_concepts',cik=None, ticker=None)
```

View the XBRL Fact Glossary [here](https://datamule.xyz/xbrl_fact_glossary) or as a csv file [here](https://datamule.xyz/static/xbrl_descriptions.csv).

#### Changing Rate Limits
The SEC.gov officially supports 10 requests / second. In practice this is not the case. After heavy experimentation the downloader's default rate limit for sec.gov has been set to 7 requests / second. If you intend to download less than 1,000 filings at a time, setting the rate limit to 10 should be fine. If you need to download more than 10,000 filings, setting the rate limit to 5 will likely avoid rate limiting. Also, downloading at off-peak times will likely let you set higher rate-limits. [Experiment Details](https://medium.com/@jgfriedman99/downloading-filings-from-the-sec-100x-faster-c38a37a59296)

```python
downloader.set_limiter('www.sec.gov', 10)
```

#### Datasets
Available datasets:
- Every [FTD](https://www.sec.gov/data-research/sec-markets-data/fails-deliver-data) since 2004. `ftd` (1.3gb, ~60s to download)
- Every [10-Q](https://www.dropbox.com/scl/fo/m7yg1eyst7oi6aqciarrd/ABrkRn0-I5nIwoM5m2wlZVg?rlkey=5qcuduan5mk4aic9wz45aqrqb&st=fetx6qnx&dl=0) since 2001. (500mb-3gb per year, ~5 minutes to download)
- Every [10-K](https://www.dropbox.com/scl/fo/ejek7n8st0x5j84xu0p4d/ACVrKdvw6j2Zv0EtpeC18ak?rlkey=lq6ouvwlbs2tfr55za2b0k0p1&st=thrzm40o&dl=0) from 2001 to September 2024. `10k_{year}` e.g. `10k_2002`. 
- Every 13F-HR Information Table since 2013. Up to the current date.
- 100,000 MD&A's since 2001. Requires [free api key](https://datamule.xyz/dashboard) *beta* 

```python
downloader.download_dataset(dataset='ftd')
downloader.download_dataset(dataset='10q_2023')
downloader.download_dataset(dataset='13f_information_table')
```

Note: Bulk datasets may become out of data. If this is the case use download_dataset() + download() to fill the gaps.
Note: 13f_information_table will always be up to date as it automatically implements this.

#### Monitoring for New Filings

Monitor for new filings using form, cik, ticker, and passing in call back functions.

```python
downloader.watch(self, interval=1, silent=True, form=None, cik=None, ticker=None, callback=None)
```

### Parsing

#### Parse SEC XBRL

Parses XBRL in JSON format to tables. [SEC XBRL](https://www.sec.gov/search-filings/edgar-application-programming-interfaces). See [Parse every SEC XBRL to csv in ten minutes](https://github.com/john-friedman/datamule-python/blob/main/examples/parse_all_xbrl.ipynb)

```python
from datamule import parse_company_concepts
table_dict_list = parse_company_concepts(company_concepts) # Returns a list of tables with labels
```

#### Parse Textual Filings into structured data

Parse textual filings into different formats. Uses [datamule parser endpoint](https://jgfriedman99.pythonanywhere.com/parse_url). If it is too slow for your use-case let me know. A faster endpoint is coming soon.

```python
# Simplified HTML
simplified_html = dm.parse_textual_filing(url='https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm', return_type='simplify')

# Interactive HTML
interactive_html = dm.parse_textual_filing(url='https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm', return_type='interactive')

# JSON
json_data = dm.parse_textual_filing(url='https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm', return_type='json')
```

### Filing Viewer

Convert parsed filing JSON into HTML with features like a table of contents sidebar:

```python
from datamule import parse_textual_filing
from datamule.filing_viewer import create_interactive_filing

data = parse_textual_filing(url='https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm', return_type='json')
create_interactive_filing(data)
```

![interactive](https://github.com/john-friedman/datamule-python/blob/main/static/interactive.png)

Try out the Filings Viewer [here](https://datamule.xyz/filings_viewer). Note: This is an older version with bugs, that will be updated with the next release of the Parser API.

### Mulebot 

Interact with SEC data using MuleBot. Mulebot uses tool calling to interface with SEC and datamule endpoints.

```python
from datamule.mulebot import MuleBot
mulebot = MuleBot(openai_api_key)
mulebot.run()
```

To use Mulebot you will need an [OpenAI API Key](https://platform.openai.com/api-keys).

#### Mulebot Server

Mulebot server is a customizable front-end for Mulebot. [Example](https://chat.datamule.xyz/)

Artifacts:
* Filing Viewer
* Company Facts Viewer
* List Viewer

Quickstart

```python
from datamule.mulebot.mulebot_server import MuleBotServer

def main():
    server = MuleBotServer()

    # Your OpenAI API key
    api_key = "sk-<YOUR_API_KEY>"
    server.set_api_key(api_key)

    # Run the server
    print("Starting MuleBotServer...")
    server.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
```

## Known Issues

- Some SEC files are malformed, which can cause parsing errors. For example, this [Tesla Form D HTML from 2009](https://www.sec.gov/Archives/edgar/data/1318605/000131860509000004/xslFormDX01/primary_doc.xml) is missing a closing `</meta>` tag.

  Workaround:
  ```python
  from lxml import etree

  with open('filings/000131860509000005primary_doc.xml', 'r', encoding='utf-8') as file:
      html = etree.parse(file, etree.HTMLParser())
  ```


## Roadmap
- [ ] add documentation for filing and parser modules
- [ ] add current names to former names
- [ ] Need to make conductor more robust. We have new options now including desc / asc
- [ ] add facet filters for forms etc
- [ ] sec search engine
- [ ] mulebot add method to use custom html templates
- [ ] mulebot - look at adding summarization. Add some protections to too many tokens being used + add options to allow summarization etc.
- [ ] Paths may be messed up on non windows devices. Need to verify.
- [ ] Analytics?
- [ ] downloader succesful downloads message may be slightly off.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the [MIT LICENSE](LICENSE).

## Change Log
[Change Log](changelog.md).

---

## Other Useful SEC Packages
- [Edgartools](https://github.com/dgunning/edgartools)
- [SEC Parsers](https://github.com/john-friedman/SEC-Parsers)
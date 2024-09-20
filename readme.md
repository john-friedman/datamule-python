# datamule

![PyPI - Downloads](https://img.shields.io/pypi/dm/datamule)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fjohn-friedman%2Fdatamule-python&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![GitHub](https://img.shields.io/github/stars/john-friedman/datamule-python)

A Python package to simplify working with SEC filings. Also includes Mulebot, an open-source chatbot for SEC data that does not require storage. Integrated with [datamule](https://datamule.xyz/)'s APIs and datasets.

<!-- Link to medium article, how to setup a SEC chatbot in 5 minutes. -->

## Features

- Monitor EDGAR for new filings
- Parse textual filings into simplified HTML, interactive HTML, or structured JSON
- Download SEC filings quickly and easily
- Access datasets such as every MD&A from 2024 or every 2024 10-K converted to structured JSON
- Interact with SEC data using MuleBot (coming soon)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Downloader](#downloader)
  - [Parsing](#parsing)
  - [Filing Viewer](#filing-viewer)
  - [MuleBot](#mulebot)
- [Datasets](#datasets)
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
pip install datamule[mulebot]  # Install with MuleBot (coming soon)
pip install datamule[all]  # Install all extras
```

Available extras:
- `filing_viewer`: Includes dependencies for the filing viewer module
- `mulebot`: Includes MuleBot for interacting with SEC data (coming soon)
- `mulebot_server`: Includes Flask server for running MuleBot (coming soon)
- `all`: Installs all available extras

## Quick Start

```python
import datamule as dm

downloader = dm.Downloader()
downloader.download(form='10-K', ticker='AAPL')
```

## Usage

### Downloader

The `Downloader` class uses the [EFTS API](https://efts.sec.gov/LATEST/search-index) to retrieve filings.

#### Downloading Filings

```python
downloader = dm.Downloader()

# Download all 10-K filings for Tesla using CIK
downloader.download(form='10-K', cik='1318605', output_dir='filings')

# Download 10-K filings for multiple companies using tickers
downloader.download(form='10-K', ticker=['TSLA', 'META'], output_dir='filings')

# Download every form 3 for a specific date
downloader.download(form='3', date='2024-05-21', output_dir='filings')
```

#### Monitoring for New Filings

```python
print("Monitoring SEC EDGAR for changes...")
changed_bool = downloader.watch(1, silent=False, cik=['0001267602', '0001318605'], form=['3', 'S-8 POS'])
if changed_bool:
    print("New filing detected!")
```

### Parsing

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
from datamule.filing_viewer import create_interactive_html

data = parse_textual_filing(url='https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm', return_type='json')
create_interactive_html(data, 'output_path.html')
```

![interactive](https://github.com/john-friedman/datamule-python/blob/main/static/interactive.png)



### Mulebot 

Interact with SEC data using MuleBot (coming soon). Mulebot uses tool calling to interface with SEC and datamule endpoints.

Features (coming soon):
* Interface with XBRL company facts
* Interface with 10-ks, etc and summarize sections.

To use Mulebot you will need an [OpenAI API Key](https://platform.openai.com/api-keys).

#### Mulebot Server

Mulebot server is a customizable front-end for Mulebot.

Features (coming soon):
* Display XBRL tables with download / copy button.
* Download XBRL tables for a specific company in ZIP.
* Display sections of filings, like MD&A with links to filing viewer and original.

Quickstart

```python
from datamule.mulebot.mulebot_server import server

def main():
    # Your OpenAI API key
    api_key = "sk-<YOUR_API_KEY>"
    server.set_api_key(api_key)

    # Run the server
    print("Starting MuleBotServer...")
    server.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
```

## Datasets

Access parsed datasets:

```python
downloader = dm.Downloader()

# Download all 2024 10-K filings converted to JSON
downloader.download_dataset('10K')

# Download all MD&As extracted from 2024 10-K filings
downloader.download_dataset('MDA')
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
- [ ] Add Mulebot
- [ ] Downloader refactor and integrate XBRL downloads

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
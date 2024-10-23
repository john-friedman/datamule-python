# datamule

![PyPI - Downloads](https://img.shields.io/pypi/dm/datamule)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fjohn-friedman%2Fdatamule-python&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![GitHub](https://img.shields.io/github/stars/john-friedman/datamule-python)

A Python package for working with SEC filings at scale. Includes [Mulebot](https://chat.datamule.xyz/), an open-source chatbot for SEC data with no storage requirements.

📚 [Full Documentation](https://john-friedman.github.io/datamule-python/) | 🌐 [Website](https://datamule.xyz/) | 📝 [Article: Deploy a Financial Chatbot in 5 Minutes](https://medium.com/@jgfriedman99/how-to-deploy-a-financial-chatbot-in-5-minutes-ef5eec973d4c)

## Key Features

- 📥 Download SEC filings quickly and efficiently
- 🔍 Monitor EDGAR for new filings in real-time
- 📊 Parse textual filings into simplified HTML, interactive HTML, or structured JSON
- 💾 Access comprehensive datasets (10-Ks, SIC codes, etc.)
- 🤖 Interact with SEC data using MuleBot

## Quick Start

```bash
# Basic installation
pip install datamule

# Install with all features
pip install datamule[all]
```

```python
import datamule as dm

# Download filings
downloader = dm.Downloader()
downloader.download(form='10-K', ticker='AAPL')

# Download filing attachments such as information tables
downloader.download(form='13F-HR',file_types=['INFORMATION TABLE'],date=('2024-09-14','2024-09-16'))

# Download every 10Q from 2023. Should take 2 minutes
downloader.download_dataset(dataset='10q_2023')
```

## Available Extras

- `filing_viewer`: Filing viewer module
- `mulebot`: SEC data interaction chatbot
- `mulebot_server`: Flask server for MuleBot
- `all`: All available features

## Resources

- 📊 [SEC Filing Glossary](https://datamule.xyz/sec_glossary)
- 📈 [XBRL Fact Glossary](https://datamule.xyz/xbrl_fact_glossary)
- 🤖 [Try MuleBot](https://chat.datamule.xyz/)

## Datasets

Access comprehensive SEC datasets including:
- Historical FTD data (since 2004)
- 10-K and 10-Q filings (since 2001)
- 13F-HR Information Tables (since 2013)
- MD&A collection (100,000+ since 2001, requires free API key)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

---

For detailed usage examples, API reference, and advanced features, please visit our [documentation](https://john-friedman.github.io/datamule-python/).

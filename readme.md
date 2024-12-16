# datamule

## 🔄 Major Update 
**Datamule has undergone a significant rework and is no longer backwards compatible. If this has affected your workflow please post on the github issues megathread. Sorry for the inconvenience.**

[![Downloads](https://static.pepy.tech/badge/datamule)](https://pepy.tech/project/datamule)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fjohn-friedman%2Fdatamule-python&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
![GitHub](https://img.shields.io/github/stars/john-friedman/datamule-python)


A Python package for working with SEC filings at scale. 📚 [Full Documentation](https://john-friedman.github.io/datamule-python/) | 🌐 [Website](https://datamule.xyz/)

## Features

- 📥 [Download SEC filings quickly and efficiently](https://john-friedman.github.io/datamule-python/usage/downloader.html)
- 🔍 [Monitor EDGAR for new filings in real-time](https://john-friedman.github.io/datamule-python/usage/monitor.html)
- 📊 [Parse filings at scale](https://john-friedman.github.io/datamule-python/usage/parsing.html)
- 💾 [Access comprehensive datasets (10-Ks, SIC codes, etc.)](https://john-friedman.github.io/datamule-python/usage/datasets.html)
- 🗃️ [Build datasets directly from unstructured text](https://john-friedman.github.io/datamule-python/usage/dataset_builder.html)
- 🤖 [Interact with SEC data using MuleBot](https://john-friedman.github.io/datamule-python/usage/mulebot.html)

## Quick Start

### Basic Installation

```bash
pip install datamule
```

### Installation with all extras
```bash
pip install datamule[all]
```


### Download submissions example

```python
from datamule import Downloader

downloader = Downloader()
downloader.download_submissions(form='10-K', ticker='AAPL')
```

## Articles:
- [How to host the SEC Archive for $20/month ](https://medium.com/@jgfriedman99/how-to-host-the-sec-archive-for-20-month-da374cc3c3fb)
- [Creating Structured Datasets from SEC filings](https://medium.com/@jgfriedman99/how-to-create-alternative-datasets-using-datamule-d3a0192da8f6)
- [Deploy a Financial Chatbot in 5 Minutes](https://medium.com/@jgfriedman99/how-to-deploy-a-financial-chatbot-in-5-minutes-ef5eec973d4c)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

---

For detailed usage examples, API reference, and advanced features, please visit our [documentation](https://john-friedman.github.io/datamule-python/).

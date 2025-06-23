# datamule
[![Downloads](https://static.pepy.tech/badge/datamule)](https://pepy.tech/project/datamule)
![GitHub Stars](https://img.shields.io/github/stars/john-friedman/datamule-python)

A python package for working with SEC filings at scale.

* [Documentation](https://john-friedman.github.io/datamule-python/datamule-python/quickstart/)


## Related:

### Packages
* [datamule-data](https://github.com/john-friedman/datamule-data/) Contains datasets for use with datamule-python
* [datamule-indicators](https://github.com/john-friedman/datamule-indicators/) Create economic indicators from SEC filings
* [txt2dataset](https://github.com/john-friedman/txt2dataset/) Create datasets from unstructured text
* [secsgml](https://github.com/john-friedman/secsgml/) Parse SEC filings in SGML format
* [doc2dict](https://github.com/john-friedman/doc2dict) Convert documents to dictionaries.
* [secxbrl](https://github.com/john-friedman/secxbrl) Fast, lightweight parser designed for SEC InLine XBRL.

### Articles/Cloud
* [Website](https://datamule.xyz)
* [SEC Census](https://github.com/john-friedman/SEC-Census)

## Installation
```
pip install datamule
```

## Quickstart
```
from datamule import Portfolio
portfolio = Portfolio('apple')
portfolio.download_submissions(ticker='AAPL',submission_type='10-K')
```

## Providers
You can use the `sec` (default) or `datamule` (no rate limit) which requires an [api key](https://john-friedman.github.io/datamule-python/datamule-python/data_provider/).

## Disclaimer
This package almost certainly solves your use case or will solve your use case soon. 

However, the docs are incomplete. Feel free to post a github issue or [email me](mailto:johnfriedman@datamule.xyz) for clarification. I reply quickly, and this helps me improve the documentation.
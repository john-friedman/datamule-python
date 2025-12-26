# datamule
[![Downloads](https://static.pepy.tech/badge/datamule)](https://pepy.tech/project/datamule)
![GitHub Stars](https://img.shields.io/github/stars/john-friedman/datamule-python)

A python package for working with SEC filings at scale. Integrated with [datamule's endpoints](https://datamule.xyz/products).

* [Documentation](https://john-friedman.github.io/datamule-python/datamule-python/examples/quickstart/)

## Datamule's Endpoints (requires API Key)

I host a bunch of useful stuff in the cloud, such as:
* SEC Websocket (Free)
* SEC Archive without rate limits ($1/100,000 downloads)
* SEC MySQL RDS ($1/million rows retrieved)
    - SEC XBRL
    - Company Fundamentals
    - Proxy Voting Records: (N-PX)
    - Institutional Holdings: (13F-HR)
    - Insider Transactions: (3,4,5)

Pricing is meant to cover usage + if I make money that's cool. 

[Get an API Key](https://datamule.xyz/dashboard2.html)

> All cloud resources are built using this package. This package is under the MIT License. You are 100% allowed to use this package to create your own commercial offerings. If you do, please let me know! I think it's neat. 

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
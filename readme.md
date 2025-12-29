# datamule
[![Downloads](https://static.pepy.tech/badge/datamule)](https://pepy.tech/project/datamule)
![GitHub Stars](https://img.shields.io/github/stars/john-friedman/datamule-python)

A python package for working with SEC filings at scale. Developed by [John Friedman](https://datamule.xyz/about).

- [Documentation](https://john-friedman.github.io/datamule-python/)
- [Quickstart](https://john-friedman.github.io/datamule-python/datamule-python/examples/quickstart/#portfolio)
- [Website](https://datamule.xyz/)


**Installation**
```
pip install datamule
```

**Quickstart**
```
from datamule import Portfolio

portfolio = Portfolio('amzn')
portfolio.download_submissions(ticker='AMZN',submission_type='10-K')
```

**Paid Integrations**

Most of this package is free and open source. But that can be slow. For convenience, datasets built using this package have been uploaded to the cloud. See [Products](https://datamule.xyz/product).

For example, you can use datamule's SEC archive to download SEC filings without rate limits at a cost of $1/100k downloads.

```
# Using the SEC w/ rate limit 5/s ~= 10 days of downloads
# Using datamule ~= 1 hour
portfolio.download_submissions(submission_type='4',provider='datamule-tar')
```
**Production**

This package is suitable for production, and can run on small machines such as aws t4g.nanos. 

[Datamule](https://datamule.xyz/)'s AWS infrastructure (concurrent ECS Fargate instances, constantly running EC2 instances) is built with this package as its core.

**Disclaimer**

This package almost certainly solves your use case or will solve your use case soon. However, the docs are incomplete. Feel free to post a github issue or [email me](mailto:johnfriedman@datamule.xyz) for clarification. I reply quickly, and this helps me improve the documentation.
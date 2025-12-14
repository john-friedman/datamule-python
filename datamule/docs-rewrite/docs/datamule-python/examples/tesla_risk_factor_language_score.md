# Tesla Risk Factor Language Score

Calculate the negative ratio of each Tesla 10-K's Item 1A: Risk Factors, using Loughran-Mcdonald.

First you need to download [budgetnlp](https://github.com/john-friedman/budgetnlp).
```bash
pip install budgetnlp
```

```python
from datamule import Portfolio
from budgetnlp import negative_ratio
import csv


portfolio = Portfolio('tesla_risk_factor_language_score')
portfolio.download_submissions(ticker='TSLA',submission_type=['10-K'],document_type=['10-K'])


data = []
for sub in portfolio:
    for doc in sub:
        if doc.type in ['10-K']:
            if doc.extension in ['.htm','.html']:
                item1a_risk_factors = doc.get_section(title='item1a', format='text')[0]
                neg_ratio = negative_ratio(item1a_risk_factors, negation_reversals=True)

                data.append({'accession':sub.accession,'document_type':doc.type,'filing_date':doc.filing_date,
                            "negative_ratio":neg_ratio, 'filer_cik' : sub._filer_cik})

with open('risk_factors_negative_ratio.csv', 'w', encoding='utf-8',newline='') as csvfile:
    fieldnames = ['accession', 'document_type', 'filing_date', 'negative_ratio', 'filer_cik']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
```

## Results

| Accession | Document Type | Filing Date | Negative Ratio | Filer CIK |
|-----------|---------------|-------------|----------------|-----------|
| 000119312511054847 | 10-K | 2011-03-03 | 0.0309 | 0001318605 |
| 000119312512081990 | 10-K | 2012-02-27 | 0.0322 | 0001318605 |
| 000119312513096241 | 10-K | 2013-03-07 | 0.0339 | 0001318605 |
| 000119312514069681 | 10-K | 2014-02-26 | 0.0319 | 0001318605 |
| 000156459015001031 | 10-K | 2015-02-26 | 0.0336 | 0001318605 |
| 000156459016013195 | 10-K | 2016-02-24 | 0.0358 | 0001318605 |
| 000156459017003118 | 10-K | 2017-03-01 | 0.0319 | 0001318605 |
| 000156459018002956 | 10-K | 2018-02-23 | 0.0316 | 0001318605 |
| 000156459019003165 | 10-K | 2019-02-19 | 0.0321 | 0001318605 |
| 000156459020004475 | 10-K | 2020-02-13 | 0.0337 | 0001318605 |
| 000156459021004599 | 10-K | 2021-02-08 | 0.0345 | 0001318605 |
| 000095017022000796 | 10-K | 2022-02-07 | 0.0391 | 0001318605 |
| 000095017023001409 | 10-K | 2023-01-31 | 0.0400 | 0001318605 |
| 000162828024002390 | 10-K | 2024-01-29 | 0.0407 | 0001318605 |
| 000162828025003063 | 10-K | 2025-01-30 | 0.0404 | 0001318605 |
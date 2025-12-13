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
# Costco Audit Complexity

Analyze the complexity of the "REPORT OF INDEPENDENT REGISTERED PUBLIC ACCOUNTING FIRM" from Costco's 10-K, using a simple formula.

```
score = (complexity_weight * complexity_ratio + uncertainty_weight * uncertainty_ratio + sentence_weight * mean_sentence_length / normal_sentence_length)
```
    

First you need to download [budgetnlp](https://github.com/john-friedman/budgetnlp).
```bash
pip install budgetnlp
```

```python
from datamule import Portfolio
from budgetnlp import negative_ratio,naive_complexity_ratio
import csv

portfolio = Portfolio('costco_audit_complexity')
portfolio.download_submissions(ticker='COST', submission_type=['10-K'], document_type=['10-K'])

data = []
for sub in portfolio:
    for doc in sub:
        if doc.type in ['10-K']:
            if doc.extension in ['.htm', '.html']:
                try:
                    audit_report = doc.get_section(title_regex='(?i)report of independent registered public accounting firm', format='text')[0]
                    complexity_score = naive_complexity_ratio(audit_report, complexity_weight=50, uncertainty_weight=30, sentence_weight=20,normal_sentence_length=20)

                    data.append({'accession': sub.accession, 'document_type': doc.type, 'filing_date': doc.filing_date,
                                "complexity_score": complexity_score, 'filer_cik': sub._filer_cik})
                except:
                    pass

with open('costco_audit_complexity.csv', 'w', encoding='utf-8', newline='') as csvfile:
    fieldnames = ['accession', 'document_type', 'filing_date', 'complexity_score', 'filer_cik']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
```

## Results

| Accession | Document Type | Filing Date | Complexity Score | Filer CIK |
|-----------|---------------|-------------|------------------|-----------|
| 000119312505223245 | 10-K | 2005-11-10 | 22.21 | 0000909832 |
| 000090983215000014 | 10-K | 2015-10-14 | 7.00 | 0000909832 |
| 000090983224000049 | 10-K | 2024-10-09 | 17.00 | 0000909832 |
| 000119312507225805 | 10-K | 2007-10-25 | 7.00 | 0000909832 |
| 000119312511271844 | 10-K | 2011-10-14 | 26.70 | 0000909832 |
| 000090983214000021 | 10-K | 2014-10-15 | 7.00 | 0000909832 |
| 000090983219000019 | 10-K | 2019-10-11 | 30.68 | 0000909832 |
| 000090983217000014 | 10-K | 2017-10-18 | 7.00 | 0000909832 |
| 000119312508211709 | 10-K | 2008-10-16 | 24.59 | 0000909832 |
| 000119312512428890 | 10-K | 2012-10-19 | 27.32 | 0000909832 |
| 000090983225000101 | 10-K | 2025-10-08 | 30.26 | 0000909832 |
| 000090983220000017 | 10-K | 2020-10-07 | 35.00 | 0000909832 |
| 000090983218000013 | 10-K | 2018-10-26 | 26.03 | 0000909832 |
| 000119312509208963 | 10-K | 2009-10-16 | 24.22 | 0000909832 |
| 000119312504195535 | 10-K | 2004-11-12 | 21.85 | 0000909832 |
| 000090983216000032 | 10-K | 2016-10-12 | 7.00 | 0000909832 |
| 000090983223000042 | 10-K | 2023-10-11 | 17.00 | 0000909832 |
| 000119312510230379 | 10-K | 2010-10-18 | 24.58 | 0000909832 |
| 000090983222000021 | 10-K | 2022-10-05 | 17.00 | 0000909832 |
| 000119312506238399 | 10-K | 2006-11-17 | 7.00 | 0000909832 |
| 000144530513002422 | 10-K | 2013-10-16 | 27.62 | 0000909832 |
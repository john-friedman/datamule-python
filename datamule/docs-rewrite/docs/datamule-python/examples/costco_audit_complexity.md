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
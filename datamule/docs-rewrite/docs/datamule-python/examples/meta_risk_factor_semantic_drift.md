# Meta Risk Factor Drift Score


Calculate the Semantic Drift of Meta 10-K Item 1A: Risk Factors over time.

First you need to download [budgetnlp](https://github.com/john-friedman/budgetnlp) and [fastembed](https://github.com/qdrant/fastembed).

```bash
pip install budgetnlp
```

```python
from datamule import Portfolio
from budgetnlp import calculate_drift_score
from fastembed import TextEmbedding
import csv

# Initialize portfolio and download Meta 10-K filings
portfolio = Portfolio('meta_risk_factor_drift')
portfolio.download_submissions(
    ticker='META',
    submission_type=['10-K'],
    document_type=['10-K']
)

# Extract risk factors from all filings
risk_factors_data = []
for sub in portfolio:
    for doc in sub:
        if doc.type == '10-K' and doc.extension in ['.htm', '.html']:
            item1a_text = doc.get_section(title='item1a', format='text')[0]
            token_count = len(item1a_text.split())
            
            risk_factors_data.append({
                'accession': sub.accession,
                'filing_date': doc.filing_date,
                'text': item1a_text,
                'token_count': token_count,
                'filer_cik': sub._filer_cik
            })

# Sort by filing date (chronological order)
risk_factors_data.sort(key=lambda x: x['filing_date'])

# Generate embeddings using FastEmbed (Qdrant)
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

texts = [item['text'] for item in risk_factors_data]
embeddings = list(model.embed(texts))

# Convert to lists (from generators/arrays)
embeddings = [list(emb) for emb in embeddings]
token_counts = [item['token_count'] for item in risk_factors_data]

drift_results = calculate_drift_score(embeddings, token_counts)

# Prepare output data
output_data = []
for i, drift in enumerate(drift_results):
    output_data.append({
        'prior_accession': risk_factors_data[i]['accession'],
        'prior_filing_date': risk_factors_data[i]['filing_date'],
        'current_accession': risk_factors_data[i + 1]['accession'],
        'current_filing_date': risk_factors_data[i + 1]['filing_date'],
        'cosine_distance': drift['cosine_distance'],
        'drift_score': drift['drift_score'],
        'current_token_count': risk_factors_data[i + 1]['token_count'],
        'filer_cik': risk_factors_data[i]['filer_cik']
    })

# Write to CSV
with open('meta_risk_factor_drift.csv', 'w', encoding='utf-8', newline='') as csvfile:
    fieldnames = [
        'prior_accession', 'prior_filing_date',
        'current_accession', 'current_filing_date',
        'cosine_distance', 'drift_score', 'current_token_count', 'filer_cik'
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_data)
```

## Results


| Prior Accession | Prior Filing Date | Current Accession | Current Filing Date | Cosine Distance | Drift Score | Current Token Count | Filer CIK |
|-----------------|-------------------|-------------------|---------------------|-----------------|-------------|---------------------|-----------|
| 000132680113000003 | 2013-02-01 | 000132680114000007 | 2014-01-31 | 0.0052 | 0.0496 | 14,560 | 0001326801 |
| 000132680114000007 | 2014-01-31 | 000132680115000006 | 2015-01-29 | 0.0026 | 0.0253 | 14,594 | 0001326801 |
| 000132680115000006 | 2015-01-29 | 000132680116000043 | 2016-01-28 | 0.0037 | 0.0355 | 15,476 | 0001326801 |
| 000132680116000043 | 2016-01-28 | 000132680117000007 | 2017-02-03 | 0.0110 | 0.1070 | 16,605 | 0001326801 |
| 000132680117000007 | 2017-02-03 | 000132680118000009 | 2018-02-01 | 0.0040 | 0.0391 | 17,190 | 0001326801 |
| 000132680118000009 | 2018-02-01 | 000132680119000009 | 2019-01-31 | 0.0001 | 0.0013 | 18,209 | 0001326801 |
| 000132680119000009 | 2019-01-31 | 000132680120000013 | 2020-01-30 | 0.0004 | 0.0042 | 21,830 | 0001326801 |
| 000132680120000013 | 2020-01-30 | 000132680121000014 | 2021-01-28 | 0.0886 | 0.8978 | 25,128 | 0001326801 |
| 000132680121000014 | 2021-01-28 | 000132680122000018 | 2022-02-03 | 0.0000 | 0.0000 | 26,293 | 0001326801 |
| 000132680122000018 | 2022-02-03 | 000132680123000013 | 2023-02-02 | 0.0017 | 0.0177 | 26,039 | 0001326801 |
| 000132680123000013 | 2023-02-02 | 000132680124000012 | 2024-02-02 | 0.0064 | 0.0659 | 27,958 | 0001326801 |
| 000132680124000012 | 2024-02-02 | 000132680125000017 | 2025-01-30 | 0.0019 | 0.0197 | 28,928 | 0001326801 |
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
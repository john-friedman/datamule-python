# General Electric Convenant Breach Risk

Extract context around keywords associated with near threshold risk, and classify. Note that this is a very basic approach, and has defects such as: 
- Model does not determine if threshold risk is associated with GE or with another company that is referenced in GE's 10-Ks.
- Model may misclassify other threshold risks with legal risks.


First you need to get a Gemini API Key and set it in your environment, as well as install txt2dataset.

```powershell
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your-api-key-here','User')
```

```bash
pip install txt2dataset
```

```python
from datamule import Portfolio
from txt2dataset import DatasetBuilder
from budgetnlp import extract_contexts
import csv
from pydantic import BaseModel
from typing import List, Literal
from collections import defaultdict

portfolio = Portfolio('ge_near_threshold_risk')
portfolio.download_submissions(ticker='GE', submission_type=['10-Q'], document_type=['10-Q'])

data = []
for sub in portfolio:
    for doc in sub:
        if doc.type in ['10-Q']:
            if doc.extension in ['.htm', '.html']:
                try:
                    # Define keywords that are associated with threshold risk.
                    keywords = [
                        "leverage",
                        "covenant",
                        "headroom",
                        "waiver",
                        "compliance",
                        "interest coverage",
                        "debt-to-EBITDA",
                        "breach",
                        "amendment",
                        "cushion",
                        "violation"
                    ]
                    # Get context around keyword matches
                    contexts = extract_contexts(doc.text, keywords, context_sentences=2)
      
                    for idx,context in enumerate(contexts):
                        data.append({'accession_id': f"{sub.accession}_{idx}", 'document_type': doc.type, 'filing_date': doc.filing_date,
                                    "context": context, 'filer_cik': sub._filer_cik})
                except:
                    pass

with open('ge_near_threshold_risk_excerpts.csv', 'w', encoding='utf-8', newline='') as csvfile:
    fieldnames = ['accession_id','document_type', 'filing_date', 'context', 'filer_cik']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)


# --- txt2dataset processing starts here ---

# Define the schema
class ConvenantBreachRiskInfo(BaseModel):
    explanation: str
    classification: Literal["FINE", "WARNING", "WAIVER", "BREACH", "UNRELATED"]

class ConvenantBreachRisk(BaseModel):
    info_found: bool
    data: List[ConvenantBreachRiskInfo] = []

# Prepare entries from the CSV
entries = []
for item in data:
    if item['context']: 
        identifier = item['accession_id']
        text = item['context']
        entries.append((identifier, text))

# Define the prompt
prompt = "Classify this text as FINE, WARNING, WAIVER, BREACH, or UNRELATED - where FINE means covenants comfortably met, WARNING means approaching covenant limits, WAIVER means covenant waiver/amendment obtained, BREACH means covenant violated, and UNRELATED means no covenant risk discussed."

# Initialize the DatasetBuilder
builder = DatasetBuilder(
    prompt=prompt,
    schema=ConvenantBreachRisk,
    model="gemini-2.5-flash-lite",
    entries=entries,
    rpm=1000
)
print(builder.api_key)

# Build the dataset
builder.build()

# Save the structured output
builder.save('ge-convenant-breach-risk.csv')



# Define severity mapping
SEVERITY_MAP = {
    'BREACH': 1.0,
    'WAIVER': 0.66,
    'WARNING': 0.33,
    'FINE': 0.0,
    'UNRELATED': 0.0
}

# Read the original excerpts CSV (has metadata)
excerpts_data = {}
with open('ge_near_threshold_risk_excerpts.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        excerpts_data[row['accession_id']] = {
            'document_type': row['document_type'],
            'filing_date': row['filing_date'],
            'context': row['context'],
            'filer_cik': row['filer_cik']
        }

# Read the classification results CSV
classifications = {}
with open('ge-convenant-breach-risk.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        accession_id = row['_id']
        classifications[accession_id] = {
            'classification': row['classification'],
            'explanation': row['explanation']
        }

# Merge the data
merged_data = []
for accession_id, excerpt_info in excerpts_data.items():
    if accession_id in classifications:
        classification_info = classifications[accession_id]
        merged_data.append({
            'accession_id': accession_id,
            'document_type': excerpt_info['document_type'],
            'filing_date': excerpt_info['filing_date'],
            'filer_cik': excerpt_info['filer_cik'],
            'context': excerpt_info['context'],
            'classification': classification_info['classification'],
            'explanation': classification_info['explanation'],
            'severity_score': SEVERITY_MAP.get(classification_info['classification'], 0.0)
        })

# Group by base accession (remove the _idx suffix)
accession_groups = defaultdict(list)
for item in merged_data:
    # Extract base accession by removing everything after the last underscore
    parts = item['accession_id'].rsplit('_', 1)
    base_accession = parts[0]
    accession_groups[base_accession].append(item)

# Find worst classification per accession
worst_per_accession = []
for base_accession, items in accession_groups.items():
    # Find the item with the highest severity score
    worst_item = max(items, key=lambda x: x['severity_score'])
    
    worst_per_accession.append({
        'accession': base_accession,
        'document_type': worst_item['document_type'],
        'filing_date': worst_item['filing_date'],
        'filer_cik': worst_item['filer_cik'],
        'worst_classification': worst_item['classification'],
        'severity_score': worst_item['severity_score'],
        'context': worst_item['context'],
        'explanation': worst_item['explanation']
    })

# Sort by filing date for easier reading
worst_per_accession.sort(key=lambda x: x['filing_date'])

# Write the final output
with open('ge_worst_covenant_risk_per_filing.csv', 'w', encoding='utf-8', newline='') as csvfile:
    fieldnames = ['accession', 'document_type', 'filing_date', 'filer_cik', 
                  'worst_classification', 'severity_score', 'context', 'explanation']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(worst_per_accession)
```

## Stats

This cost ~$0.001 to run.
```
Dataset building complete!
Successful: 394
Errors: 0
Unprocessed: 0
Total results: 388
Total tokens used: 47,613
Saved 388 records to ge-convenant-breach-risk.csv
```

## Results

| accession | document_type | filing_date | filer_cik | worst_classification | severity_score | context | explanation |
|-----------|---------------|-------------|-----------|---------------------|----------------|---------|-------------|
| 000004054523000238 | 10-Q | 2023-10-24 | 0000040545 | BREACH | 1.0 | In 2015, we acquired the Steam Power, Renewables and Grid businesses from Alstom, which prior to our acquisition were the subject of significant cases involving anti-competitive activities and improper payments. We had reserves of $416 million and $455 million at September 30, 2023 and December 31, 2022, respectively, for legal and compliance matters related to the legacy business practices that were the subject of cases in various jurisdictions. Allegations in these cases relate to claimed anti-competitive conduct or improper payments in the pre-acquisition period as the source of legal violations or damages. Given the significant litigation and compliance activity related to these matters and our ongoing efforts to resolve them, it is difficult to assess whether the disbursements will ultimately be consistent with the reserve established. The estimation of this reserve may not reflect the full range of uncertainties and unpredictable outcomes inherent in litigation and investigations of this nature, and at this time we are unable to develop a meaningful estimate of the range of reasonably possible additional losses beyond the amount of this reserve. | The text discusses significant legal and compliance matters related to past acquisitions, including anti-competitive activities and improper payments. While reserves have been established for these issues, the text explicitly states that it is difficult to assess whether disbursements will be consistent with the reserve and that a meaningful estimate of potential additional losses beyond the reserve cannot be developed. This indicates a high degree of uncertainty and potential for significant financial impact, which points towards a covenant breach or a very high risk of one, rather than a comfortable adherence or a mere warning. |
| 000004054524000113 | 10-Q | 2024-04-23 | 0000040545 | BREACH | 1.0 | The termination of one or more of our government contracts, or the occurrence of performance delays, cost overruns (due to inflation or otherwise), product failures, shortages in materials, components or labor, or other failures to perform to customer expectations and contract requirements could negatively impact our reputation, competitive position and financial results. In addition, our government contracts are subject to extensive procurement regulations, and new regulations or changes to existing requirements could increase our compliance costs. We are also subject to U. | The text discusses potential negative impacts on financial results due to contract issues like performance delays, cost overruns, product failures, and shortages. It also mentions the risk of increased compliance costs due to procurement regulations. These points highlight potential risks and challenges associated with meeting contract requirements, which could lead to covenant breaches if they significantly impact financial health or operational capacity. However, the text does not explicitly state that any covenant has been violated, is approaching limits, has been waived, or is comfortably met. Instead, it outlines general risks that *could* lead to issues. Therefore, it points towards potential future problems without confirming current covenant status. |
| 000004054524000176 | 10-Q | 2024-07-23 | 0000040545 | FINE | 0.0 | Substantially all of the Company's debt agreements in place at June 30, 2024 do not contain material credit rating covenants. Our unused back-up revolving syndicated credit facility contain a customary net debt-to-EBITDA financial covenant, which we satisfied at June 30, 2024. | |
# General Motors Impairment Event

Convert text data into columnar data using [txt2dataset](https://github.com/john-friedman/txt2dataset).

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
import csv
from pydantic import BaseModel
from typing import Optional, List


portfolio = Portfolio('general_motors_impairment')
portfolio.download_submissions(ticker='GM', submission_type=['8-K'], document_type=['8-K'])

data = []
for sub in portfolio:
    for doc in sub:
        if doc.type in ['8-K']:
            if doc.extension in ['.htm', '.html']:
                try:
                    # Get Item 2.06: Material Impairments
                    item206 = doc.get_section(title='item2.06', format='text')[0]
           
                    data.append({'accession': sub.accession, 'document_type': doc.type, 'filing_date': doc.filing_date,
                                "item206": item206, 'filer_cik': sub._filer_cik})
                except:
                    pass

with open('general_motors_item_206.csv', 'w', encoding='utf-8', newline='') as csvfile:
    fieldnames = ['accession', 'document_type', 'filing_date', 'item206', 'filer_cik']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

# --- txt2dataset processing starts here ---

# Define the schema
class ImpairmentInfo(BaseModel):
    expected_impairment_amount: Optional[float] = None  # Average amount in dollars
    asset_class: Optional[str] = None  # e.g., "Equity investment", "Goodwill", "PPE", "Intangibles"
    segment: Optional[str] = None  # e.g., "China", "North America"

class ImpairmentExtraction(BaseModel):
    info_found: bool
    data: List[ImpairmentInfo] = []

# Prepare entries from the CSV
entries = []
for item in data:
    if item['item206']:  # Only process if there's Item 2.06 text
        identifier = item['accession']
        text = item['item206']
        entries.append((identifier, text))

# Define the prompt
prompt = "Extract the impairment amount (as an average if a range is given), asset class (such as equity investment, goodwill, PPE, or intangibles), and business segment from this text."

# Initialize the DatasetBuilder
builder = DatasetBuilder(
    prompt="Extract impairment and restructuring charge information from this SEC filing",
    schema=ImpairmentExtraction,
    model="gemini-2.5-flash-lite",
    entries=entries,
    rpm=1000
)
print(builder.api_key)

# Build the dataset
builder.build()

# Save the structured output
builder.save('gm_impairments_structured.csv')
```

## Results

| ID | Asset Class | Expected Impairment Amount | Segment |
|----|-------------|---------------------------|---------|
| 000119312524270298 | equity interest | $2,750,000,000 | China JVs |
| 000119312524270298 | equity interest | $2,700,000,000 | China JVs |
| 000146785825000136 | electric vehicles capacity | $1,200,000,000 | GM North America |

Note that the first row is an average of `$2.6–2.9 billion` and the second row is `additional equity losses of approximately $2.7 billion`

First two rows input text:
```
General Motors Company (the “Company”, “we” or “our”) owns an equity interest in SAIC General Motors Corporation Limited (“SGM”), a 50-50 joint venture with SAIC Motor Corp., Ltd. (“SAIC”), and an equity interest in SAIC-GMAC Automotive Finance Company Limited (“SAIC-GMAC”). SGM conducts automotive operations in China through various other joint ventures with GM (together with SGM and SAIC-GMAC, the “China JVs”). On December 2, 2024, the Audit Committee of the Board of Directors of the Company concluded a material impairment of the Company’s interest in SGM was required based on a determination that a material loss in value of our investments in certain of the China JVs is other than temporary in light of the finalization of a new business forecast and certain restructuring actions that SGM is finalizing that are expected to be taken to address market challenges and competitive conditions. The Company is in the process of assessing the impact of SGM’s planned restructuring actions and recent efforts to stabilize market share and focus on profitability, and expects to (i) record an other than temporary impairment of our equity interest in the China JVs in the range of $2.6–2.9 billion in the three months ending December 31, 2024, and (ii) recognize additional equity losses of approximately $2.7 billion resulting from the implementation of SGM’s restructuring plan, which include impairment charges to be recognized by the China JVs related to plant closures and portfolio optimization, the majority of which we expect to record in the three months ending December 31, 2024. The charges are expected to be non-cash in nature and treated as special for EBIT-adjusted purposes.
```
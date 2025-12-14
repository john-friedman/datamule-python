# Late Filing Reasons

Extract the reasons why 10-Ks are delayed for a basket of companies.

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
from typing import Literal, List


portfolio = Portfolio('late_filing_persistence')
portfolio.download_submissions(cik=[1849635,1138639,1391127,730272,1467858],
                                submission_type=['NT 10-K'], document_type=['NT 10-K'])

data = []
for sub in portfolio:
    for doc in sub:
        if doc.type in ['NT 10-K']:
            if doc.extension in ['.htm', '.html']:
                try:
                    narrative = doc.get_section(title='partiii', format='text')[0]
                    data.append({'accession': sub.accession, 'document_type': doc.type, 'filing_date': doc.filing_date,
                                "narrative": narrative, 'filer_cik': sub._filer_cik})
                except:
                    pass

with open('late_filing_narratives.csv', 'w', encoding='utf-8', newline='') as csvfile:
    fieldnames = ['accession', 'document_type', 'filing_date', 'narrative', 'filer_cik']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)


# --- txt2dataset processing starts here ---

# Define the schema
class DelayInfo(BaseModel):
    type_of_delay: Literal[
        "accounting issues",
        "auditor delay", 
        "internal control weaknesses",
        "acquisition integration",
        "internal review delays",
        "other reasons"
    ]  
    explanation: str 

class DelayExtraction(BaseModel):
    info_found: bool
    data: List[DelayInfo] = []

# Prepare entries from the CSV
entries = []
for item in data:
    if item['narrative']:
        identifier = item['accession']
        text = item['narrative']
        entries.append((identifier, text))

# Define the prompt
prompt = "Extract the type of delay (such as auditor delay, accounting issues, internal control weaknesses, system failure, or other reasons) and the specific explanation for why the 10-K filing was delayed from this text."

# Initialize the DatasetBuilder
builder = DatasetBuilder(
    prompt=prompt,
    schema=DelayExtraction,
    model="gemini-2.5-flash-lite",
    entries=entries,
    rpm=1000
)
print(builder.api_key)

# Build the dataset
builder.build()

# Save the structured output
builder.save('nt10k_delay_reasons.csv')


# --- Merge metadata with extracted delay info ---

# Read the original narratives CSV (has metadata)
narratives_data = {}
with open('late_filing_narratives.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        narratives_data[row['accession']] = {
            'document_type': row['document_type'],
            'filing_date': row['filing_date'],
            'filer_cik': row['filer_cik']
        }

# Read the delay extraction results CSV
delay_extractions = {}
with open('nt10k_delay_reasons.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        accession = row['_id']
        delay_extractions[accession] = {
            'type_of_delay': row['type_of_delay'],
            'explanation': row['explanation']
        }

# Merge the data
final_data = []
for accession, metadata in narratives_data.items():
    if accession in delay_extractions:
        delay_info = delay_extractions[accession]
        final_data.append({
            'accession': accession,
            'document_type': metadata['document_type'],
            'filing_date': metadata['filing_date'],
            'filer_cik': metadata['filer_cik'],
            'type_of_delay': delay_info['type_of_delay'],
            'explanation': delay_info['explanation']
        })

# Sort by filing date
final_data.sort(key=lambda x: x['filing_date'])

# Write the final output
with open('nt10k_final_dataset.csv', 'w', encoding='utf-8', newline='') as csvfile:
    fieldnames = ['accession', 'document_type', 'filing_date', 'filer_cik', 'type_of_delay', 'explanation']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_data)
```

## Results

| Accession | Document Type | Filing Date | Filer CIK | Type of Delay | Explanation |
|-----------|--------------|-------------|-----------|---------------|-------------|
| 000119312510069519 | NT 10-K | 2010-03-29 | 0001467858 | accounting issues | The company is unable to file its Annual Report on Form 10-K for the fiscal year ended December 31, 2009 because it is still finalizing its fresh-start adjustments required by generally accepted accounting principles relating to the assets acquired and liabilities assumed from General Motors Corporation ("Old GM") in connection with Old GM's sale of assets under Section 363 of the United States Bankruptcy Code. Due to the size of the Company, the global application of fresh-start reporting and the associated determination of the fair value of its assets and liabilities is a significant undertaking, which requires extra time. |
| 000119312515074283 | NT 10-K | 2015-03-03 | 0000730272 | acquisition integration | The Company moved to a Large Accelerator Filer (LAF) for the first time in 2015 and is unable to meet the LAF due date of March 2, 2015 without unreasonable effort and expense, due primarily to the ongoing integration of the business of Refine Technology, LLC, which it acquired in June 2014, into its facilities and financial systems. The Company requires the additional time to finalize its financial statements for fiscal year 2014. |
| 000113863919000017 | NT 10-K | 2019-02-26 | 0001138639 | acquisition integration | The complex process required to prepare the Company's consolidated financial statements following the acquisition of Coriant and the significant demands related to the acquisition that diverted management time and resources from the Company's normal process of preparing and reviewing the Form 10-K. |
| 000113863921000020 | NT 10-K | 2021-02-24 | 0001138639 | internal review delays | delays in compiling and reviewing certain information included in the Form 10-K. |
| 000119312522091951 | NT 10-K | 2022-03-31 | 0001849635 | auditor delay | The Registrant's independent registered public accounting firm is in the process of completing the audit of the financial statements for the period ended December 31, 2021 and will need additional time to complete its audit. |
| 000119312523068491 | NT 10-K | 2023-03-13 | 0001391127 | accounting issues | The company is restating previously issued financial statements due to an error in accounting for sales of Edgio's Open Edge solution. The review and preparation of the restatements are ongoing. |
| 000119312523089560 | NT 10-K | 2023-04-03 | 0001849635 | accounting issues | The Registrant's accounting staff needs additional time to prepare the financial statements for the period ended December 31, 2022. |
| 000113863924000044 | NT 10-K | 2024-02-29 | 0001138639 | auditor delay | Ernst & Young LLP raised questions regarding the Company's stand-alone sales price ("SSP") methodology as it relates to revenue allocation between product revenue and certain components of services revenue, and the sufficiency of documentation retained by the Company related to the revenue portion of its quote to cash cycle and its inventory cycle. The Public Company Accounting Oversight Board had commenced an inspection of EY's audit of the Company's consolidated financial statements for the fiscal year ended December 31, 2022. |
| 000119312524069313 | NT 10-K | 2024-03-18 | 0001391127 | auditor delay | The company's previous independent registered public accounting firm resigned, and the onboarding of a new audit team to familiarize itself with the company's accounting and financial processes caused a delay in the completion of the public company audit and the filing of the annual report on Form 10-K. |
| 000119312525038175 | NT 10-K | 2025-02-27 | 0001138639 | internal review delays | Delays in compiling and reviewing certain information included in the Form 10-K. |
| 000119312525044191 | NT 10-K | 2025-03-03 | 0000730272 | auditor delay | The Company requires additional time to complete the procedures relating to its year-end reporting process, including the completion of the audit of the Company's financial statements by the Company's independent auditors for inclusion in the 2024 Form 10-K. |

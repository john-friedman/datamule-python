# Construct SEC Documents

The package [secfiler](https://github.com/john-friedman/secfiler) can be used to construct SEC filings by feeding in tabular data, such as the kind a company might have in excel spreadsheets.

## Quickstart
```
pip install secfiler
```

```
from secfiler import construct_document

rows = [
  {"footnoteText": "Contributions to non-profit organizations.", "footnoteId": "F1", "_table": "345_footnote"},
  {"aff10B5One": "0", "documentType": "4", "notSubjectToSection16": "0", "periodOfReport": "2025-08-28", "remarks": None, "schemaVersion": "X0508", "issuerCik": "0001018724", "issuerName": "AMAZON COM INC", "issuerTradingSymbol": "AMZN", "_table": "345"},
  {"signatureDate": "2025-09-02", "signatureName": "/s/ PAUL DAUBER, attorney-in-fact for Jeffrey P. Bezos, Executive Chair", "_table": "345_owner_signature"},
  {"rptOwnerCity": "SEATTLE", "rptOwnerState": "WA", "rptOwnerStateDescription": None, "rptOwnerStreet1": "P.O. BOX 81226", "rptOwnerStreet2": None, "rptOwnerZipCode": "98108-1226", "rptOwnerCik": "0001043298", "rptOwnerName": "BEZOS JEFFREY P", "isDirector": "1", "isOfficer": "1", "isOther": "0", "isTenPercentOwner": "0", "officerTitle": "Executive Chair", "_table": "345_reporting_owner"},
  {"securityTitleValue": "Common Stock, par value $.01  per share", "equitySwapInvolved": "0", "transactionCode": "G", "transactionFormType": "4", "transactionDateValue": "2025-08-28", "directOrIndirectOwnershipValue": "D", "sharesOwnedFollowingTransactionValue": "883258188", "transactionAcquiredDisposedCodeValue": "D", "transactionPricePerShareValue": "0", "transactionSharesValue": "421693", "transactionCodingFootnoteIdId": "F1", "_table": "345_non_derivative_transaction"},
]

xml_bytes = construct_document(rows, '4')
with open('bezosform4.xml', 'wb') as f:
            f.write(xml_bytes)
```

## Testing efficacy with datamule

To test how well this works, we can take data from the SEC, convert it using datamule to tabular format, and convert back.

```python
from datamule import Submission
from secfiler import construct_document

sub = Submission(url='https://www.sec.gov/Archives/edgar/data/789019/000078901926000028/0000789019-26-000028.txt')

for doc in sub:
    if doc.type == '4':
        with open('original.xml', 'wb') as f:
            f.write(doc.content)
        xml = construct_document(doc.tables, '4')
        with open('reconstructed.xml', 'wb') as f:
            f.write(xml)
```

Works pretty well! 

## Testing at scale

Requires an API key. Change document type to whatever xml file you would like.

```python

DOCUMENT_TYPE = "SH-ER" # change to whatever document you would like.

import urllib.request
import polars as pl
from datamule import Document
from datamule.utils.convenience import construct_document_url
from secfiler import construct_document


def fetch_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "John Smith johnsmith@company.com"})
    return urllib.request.urlopen(req).read()

def get_samples(document_type, n=1):
    docs = (
        pl.scan_parquet("complete_sec_documents_table.parquet")
        .filter(
            (pl.col("documentType") == document_type) &
            (pl.col("filename").str.ends_with(".xml"))
        )
        .select("accessionNumber", "filename")
        .limit(n)
    )

    rows = (
        docs.join(
            pl.scan_parquet("complete_sec_accession_cik_table.parquet")
            .select("accessionNumber", "cik"),
            on="accessionNumber",
            how="left",
        )
        .collect()
        .to_dicts()
    )

    return [
        construct_document_url(row["accessionNumber"], row["cik"], row["filename"])
        for row in rows
    ]




for url in get_samples(DOCUMENT_TYPE):
    content = fetch_url(url)
    doc = Document(type=DOCUMENT_TYPE, content=content, filename="placeholder.xml", accession="0000000000-00-000000", filing_date="2000-01-01")
    print(type(doc.tables))

    with open("original.xml", "wb") as f:
        f.write(content)

    xml = construct_document(doc.tables, DOCUMENT_TYPE)
    with open("reconstructed.xml", "wb") as f:
        f.write(xml)
```
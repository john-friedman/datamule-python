# Parse any SEC XML file

Datamule has integrated the columnar mappings of all SEC xml files (100+ unique types). See: [Reverse Engineering Columnar Mappings of all SEC XML Files
](https://github.com/john-friedman/Reverse-Engineering-Columnar-Mappings-of-all-SEC-XML-Files).

Simply substitute the document_type for that of your choosing. 

```
from datamule import Portfolio
import csv

portfolio = Portfolio('1z')
portfolio.download_submissions(document_type='1-Z') # downloads only document_type = '1-Z'

all_1z_tables = {}

for sub in portfolio:
    for doc in sub:
        if doc.extension == '.xml':
            for table in doc.tables:
                if table.name not in all_1z_tables:
                    all_1z_tables[table.name] = []
                all_1z_tables[table.name].extend(table.data)

for table_name, rows in all_1z_tables.items():
    with open(f'{table_name}.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
```

# SEC Form 1-Z Filings

| Issuer Name | City | State | Securities Class | Commission File # | Phone | Zip | Signer | Title | Offering Commence Date | Securities Sold | Net Proceeds | Price/Security | Legal Fees | Legal Firm | Auditor Fees | Auditor Firm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M&M Media, Inc. | Stamford | CT | Class B Common Stock | 024-11455 | 917-587-4981 | 06902 | /s/ Gary Mekikian | CEO | 03-31-2021 | 3,220,882 | $2,961,956.00 | $1.0028 | $54,000.00 | Crowdcheck | $157,242.00 | DBBMckennon |
| Birgo Reiturn Fund LLC | Pittsburgh | PA | Common Units of Membership Interest | 024-11783 | 412-567-1324 | 15233 | /s/ Andrew Reichert | Birgo Reiturn Fund Manager LLC, its manager | 09-27-2022 | 0 | — | $100.0000 | — | — | — | — |
| Steward Realty Trust, Inc. | Easton | MD | Class B Common Stock | 024-10925 | 503-868-0400 | 21601 | Daniel Miller | CEO | 03-15-2019 | 37,725 | — | $10.0000 | $155,000.00 | Office of John F. Woods | $7,000.00 | dbbMckennon |
| Compound Projects, LLC | New York | NY | Series #Illume | 024-11133 | 212-401-6930 | 10017 | /s/ Janine Yorio | Chief Executive Officer | 04-06-2020 | 10,140 | $48,185.00 | $4.8000 | $30,000.00 | Bevilacqua PLLC | $20,000.00 | Artesian CPA, LLC |
| Black Bird Biotech, Inc. | Flower Mound | TX | — | 024-11215 | 833-223-4204 | 75028 | Fabian G. Deneault | President | 08-04-2020 | 22,762,500 | $847,850.00 | $0.0400 | $5,000.00 | Newlan Law Firm, PLLC | $6,500.00 | Farmer Fuqua & Huff, P.C. |
| CF Fund II, LLC | Allentown | PA | — | 024-10732 | 484-712-7372 | 18104-9109 | N/A | N/A | 03-28-2021 | 54 | $5,965,819.00 | $50,000.0000 | $186,046.00 | Geraci Law Firm / Buchalter APC | $62,441.00 | Spiegel Accountancy Corp. |
| Masterworks 184, LLC | New York | NY | Class A Ordinary Shares | 024-12054 | 203-518-5172 | 10281 | /s/ Josh Goldestein | General Counsel, Secretary and Member of the Board of Managers | — | — | — | — | — | — | — | — |
| NITCHES INC | Las Vegas | NV | Common Stock | 024-11601 | 678-999-6242 | 89128 | John Morgan | President | 10-07-2021 | 44,000,000 | — | $0.0283 | $10,000.00 | Esq. | — | — |
| Masterworks 025, LLC | New York | NY | Class A Ordinary Shares | 024-11287 | 203-518-5172 | 10281 | /s/ Josh Goldestein | General Counsel, Secretary and Member of the Board of Managers | — | — | — | — | — | — | — | — |
| MAISON LUXE, INC. | Fort Lee | NJ | Common Stock | 024-11833 | 551-486-3980 | 07024 | /s/ Anil Idnani | CEO | 05-13-2022 | 96,800,000 | — | $0.0048 | $5,000.00 | Newlan Law Firm, PLLC | — | — |
| Winning Brands Corp. | Barrie | A6 | — | 024-11935 | 705-737-4062 | L4N 9J2 | /s/ Eric Lehner | Chief Executive Officer | 12-29-2022 | 656,666,666 | $185,000.00 | $0.0003 | $15,000.00 | JDT Legal, PLLC | — | — |
| Virtuix Holdings Inc. | Austin | TX | Series A Preferred Stock | 024-10511 | 8322603337 | 78758 | Jan Goetgeluk | Chief Executive Officer | 03-22-2016 | 3,142,917 | $6,894,284.00 | $2.33 | $35,000.00 | KHLK LLP | $6,000.00 | Artesian CPA |
| GROUNDFLOOR FINANCE INC. | Atlanta | GA | — | 024-10496 | 404-850-9225 | 30308 | /s/ Nick Bhargava | Executive Vice President, Secretary | 12-15-2015 | 34,936,550 | — | $10.0000 | — | Smith Anderson; Robbins Ross | $50,000.00 | Hughes Pittman & Gupton, LLP |
| VALIANT EAGLE, INC. | Woodland Hills | CA | Common Stock, par value $0.0001 | 024-11526 | 747-444-1542 | 91367 | /s/ Xavier Mitchell | Chief Executive Officer | 06-10-2021 | 662,341,267 | $2,653,552.70 | $0.0041 | $35,000.00 | Suares & Associates | — | — |
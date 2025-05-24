# Submission Types

Datamule currently can parse any html or xml document, as well as most PDF documents thanks to [doc2dict](https://github.com/john-friedman/doc2dict), which was written to support the [datamule](project). 

The result is a nested dictionary such as this [Parsed Microsoft 10-K](https://github.com/john-friedman/doc2dict/blob/main/example_output/html/dict.json).

These dictionaries are further *standardized* using [doc2dict](https://github.com/john-friedman/doc2dict)'s *mapping dict* feature. What *standardized* means is that e.g. 'ITEM 1A RISK FACTORS' is cleaned to 'item1a' to allow easy programmatic extraction.

Below is the skeleton of what will be a complete glossary of every SEC submission type, with the corresponding document types. 

Information will include:
1. Short Description of the submission type & document type.
2. Whether the document type has been standardized.

> **Note:** There are a lot of SEC Submissions & Document Types. In the interests of preserving my sanity, I will be heavily using Claude Extended to standardize my notes on this page. I have a lot of documents to read, and many pages of technical pdfs.

> **Note:** I plan to create a timeline for each document for when it is in xml, html, pdf, txt form etc to reflect changes in SEC system. This will be done using a de facto method done through parsing every file.

[Google Sheets](https://docs.google.com/spreadsheets/d/1SPRhNh-CwOhG7R9lvuR5xsXJlxW8ZTHcKSWPSRY-zQE/edit?usp=sharing)

## 1-A-W

### 1-A-W

## 1-A

### 1-A

This is XML, so should have table conversion but keys need to be standardized.

### PART II AND III

Looks standardizable. Not sure what items to standardize.

### EX1A-11 CONSENT

### EX1A-12 OPN CNSL

### EX1A-3 HLDRS RTS

### EX1A-4 SUBS AGMT

## 1

### 1

Paper. (Looks like nicely formatted PDF)

## 1-K

[Instructions](https://www.sec.gov/files/form1-k.pdf)

### 1-K

XML.

### PART II

- Item 1. Business
- Item 2. Management's Discussion and Analysis of Financial Condition and Results of Operations
- Item 3. Directors and Officers
- Item 4. Security Ownership of Management and Certain Securityholders
- Item 5. Interest of Management and Others in Certain Transactions
- Item 6. Other Information
- Item 7. Financial Statements

### EX1K-11 CONSENT

## 1-SA

I can't find good documentation on this online. Wayback machine saved a [version](https://web.archive.org/web/20250406031858/https://www.sec.gov/files/form1-sa.pdf) of the official documentation, but it's clearly incomplete.

### 1-SA

Standardized, but not sure what the items are due to variation between documents.

[See](https://www.sec.gov/Archives/edgar/data/1867925/000149315224038805/form1-sa.htm) and [this](https://www.sec.gov/Archives/edgar/data/1925674/000192567425000003/f1-sa2024.htm).

## 1-U

[Instructions](https://www.sec.gov/files/form1-u.pdf)

### 1-U

- Item 1. Fundamental Changes
- Item 2. Bankruptcy or Receivership
- Item 3. Material Modification to Rights of Securityholders
- Item 4. Changes in Issuer's Certifying Accountant
- Item 5. Non-reliance on Previously Issued Financial Statements or a Related Audit Report or Completed Interim Review
- Item 6. Changes in Control of Issuer
- Item 7. Departure of Certain Officers
- Item 8. Certain Unregistered Sales of Equity Securities
- Item 9. Other Events
- Signatures

## 1-Z

### 1-Z

XML.

## 10-12B

[Instructions](https://www.sec.gov/files/form10-12b.pdf)

### 10-12B

- Item 1. Business
- Item 1A. Risk Factors
- Item 2. Financial Information
- Item 3. Properties
- Item 4. Security Ownership of Certain Beneficial Owners and Management
- Item 5. Directors and Executive Officers
- Item 6. Executive Compensation
- Item 7. Certain Relationships and Related Transactions, and Director Independence
- Item 8. Legal Proceedings
- Item 9. Market Price of and Dividends on the Registrant's Common Equity and Related Stockholder Matters
- Item 10. Recent Sales of Unregistered Securities
- Item 11. Description of Registrant's Securities to be Registered
- Item 12. Indemnification of Directors and Officers
- Item 13. Financial Statements and Supplementary Data
- Item 14. Changes in and Disagreements with Accountants on Accounting and Financial Disclosure
- Item 15. Financial Statements and Exhibits
- Signatures

## 10-12G

[Instructions](https://www.sec.gov/files/form10-12g.pdf)

### 10-12G

- Item 1. Business
- Item 1A. Risk Factors
- Item 2. Financial Information
- Item 3. Properties
- Item 4. Security Ownership of Certain Beneficial Owners and Management
- Item 5. Directors and Executive Officers
- Item 6. Executive Compensation
- Item 7. Certain Relationships and Related Transactions, and Director Independence
- Item 8. Legal Proceedings
- Item 9. Market Price of and Dividends on the Registrant's Common Equity and Related Shareholder Matters
- Item 10. Recent sales of Unregistered Securities
- Item 11. Description of Registrant's Securities to Be Registered
- Item 12. Indemnification of Directors and Officers
- Item 13. Financial Statements and Supplementary Data
- Item 14. Changes in and Disagreements with Accountants on Accounting and Financial Disclosure
- Item 15. Financial Statements and Exhibits
- Signatures

## 10-D

[Instructions](https://www.sec.gov/files/form10d.pdf)

### 10-D

**PART I – DISTRIBUTION INFORMATION**
- Item 1. Distribution and Pool Performance Information
- Item 1A. Asset-Level Information
- Item 1B. Asset Representations Reviewer and Investor Communication

**PART II – OTHER INFORMATION**
- Item 2. Legal Proceedings
- Item 3. Sales of Securities and Use of Proceeds
- Item 4. Defaults Upon Senior Securities
- Item 5. [Reserved]
- Item 6. Significant Obligors of Pool Assets
- Item 7. Change in Sponsor Interest in the Securities
- Item 8. Significant Enhancement Provider Information
- Item 9. Other Information
- Item 10. Exhibits
- Signatures

## 10-K

[Instructions](https://www.sec.gov/files/form10-k.pdf)

### 10-K

**Part I:**
- Item 1. Business
- Item 1A. Risk Factors
- Item 1B. Unresolved Staff Comments
- Item 1C. Cybersecurity
- Item 2. Properties
- Item 3. Legal Proceedings
- Item 4. Mine Safety Disclosures

**Part II:**
- Item 5. Market for Registrant's Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities
- Item 6. [Reserved]
- Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations
- Item 7A. Quantitative and Qualitative Disclosures About Market Risk
- Item 8. Financial Statements and Supplementary Data
- Item 9. Changes in and Disagreements With Accountants on Accounting and Financial Disclosure
- Item 9A. Controls and Procedures
- Item 9B. Other Information
- Item 9C. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections

**Part III:**
- Item 10. Directors, Executive Officers and Corporate Governance
- Item 11. Executive Compensation
- Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters
- Item 13. Certain Relationships and Related Transactions, and Director Independence
- Item 14. Principal Accountant Fees and Services

**Part IV:**
- Item 15. Exhibits and Financial Statement Schedules
- Item 16. Form 10-K Summary

**Signatures**

## 10-KT
### 10-KT
[See 10-K](#10-k)

## 10-Q

[Instructions](https://www.sec.gov/files/form10-q.pdf)

### 10-Q

**Part I:**
- Item 1. Financial Statements
- Item 2. Management's Discussion and Analysis of Financial Condition and Results of Operations
- Item 3. Quantitative and Qualitative Disclosures About Market Risk
- Item 4. Controls and Procedures

**Part II:**
- Item 1. Legal Proceedings
- Item 1A. Risk Factors
- Item 2. Unregistered Sales of Equity Securities and Use of Proceeds
- Item 3. Defaults Upon Senior Securities
- Item 4. Mine Safety Disclosures
- Item 5. Other Information
- Item 6. Exhibits

**Signatures**

## 11-K

### 11-K

Doesn't seem standardizable.

## 13F-HR

### 13F-HR

XML.

### INFORMATION TABLE

XML.

## 13F-NT

### 13F-NT

XML.

## 144

### 144

XML.

## 15-12G

### 15-12G

Short html document - no need to standardize?

## 15-15D

### 15-15D

Short html document - no need to standardize?

## 15F-12B

### 15F-12B

**PART I**
- Item 1. Exchange Act Reporting History
- Item 2. Recent United States Market Activity
- Item 3. Foreign Listing and Primary Trading Market
- Item 4. Comparative Trading Volume Data
- Item 5. Alternative Record Holder Information
- Item 6. Debt Securities
- Item 7. Notice Requirement
- Item 8. Prior Form 15 Filers

**PART II**
- Item 9. Rule 12g3-2(b) Exemption

**PART III**
- Item 10. Exhibits
- Item 11. Undertakings
- Signatures

## 15F-15D

### 15F-15D

Short html document - no need to standardize?

## 17AD-27

### 17AD-27

Doesn't seem standardizable.

## 18-K

### 18-K

Might be standardizable.

## 19B-4E

### 19B-4E

No documents with information in the SEC archive. Think I need to use the other archive.

## 20-F

[Instructions](https://www.sec.gov/files/form20-f.pdf)

### 20-F

Note: This can be standardized much more. Lot of subsections that are standardized.

**PART I**
- Item 1. Identity of Directors, Senior Management and Advisers
  - A. Directors and senior management
  - B. Advisers
  - C. Auditors
- Item 2. Offer Statistics and Expected Timetable
  - A. Offer statistics
  - B. Method and expected timetable
- Item 3. Key Information
  - A. Reserved
  - B. Capitalization and indebtedness
  - C. Reasons for the offer and use of proceeds
  - D. Risk factors
- Item 4. Information on the Company
  - A. History and development of the company
  - B. Business overview
  - C. Organizational structure
  - D. Property, plants and equipment
- Item 4A. Unresolved Staff Comments
- Item 5. Operating and Financial Review and Prospects
  - A. Operating results
  - B. Liquidity and capital resources
  - C. Research and development, patents and licenses, etc
  - D. Trend information
  - E. Critical Accounting Estimates
- Item 6. Directors, Senior Management and Employees
  - A. Directors and senior management
  - B. Compensation
  - C. Board practices
  - D. Employees
  - E. Share ownership
  - F. Disclosure of a registrant's action to recover erroneously awarded compensation
- Item 7. Major Shareholders and Related Party Transactions
  - A. Major shareholders
  - B. Related party transactions
  - C. Interests of experts and counsel
- Item 8. Financial Information
  - A. Consolidated Statements and Other Financial Information
  - B. Significant Changes
- Item 9. The Offer and Listing
  - A. Offer and listing details
  - B. Plan of distribution
  - C. Markets
  - D. Selling shareholders
  - E. Dilution
  - F. Expenses of the issue
- Item 10. Additional Information
  - A. Share capital
  - B. Memorandum and articles of association
  - C. Material contracts
  - D. Exchange controls
  - E. Taxation
  - F. Dividends and paying agents
  - G. Statement by experts
  - H. Documents on display
  - I. Subsidiary Information
  - J. Annual Report to Security Holders
- Item 11. Quantitative and Qualitative Disclosures About Market Risk
- Item 12. Description of Securities Other than Equity Securities
  - A. Debt Securities
  - B. Warrants and Rights
  - C. Other Securities
  - D. American Depositary Shares

**PART II**
- Item 13. Defaults, Dividend Arrearages and Delinquencies
- Item 14. Material Modifications to the Rights of Security Holders and Use of Proceeds
- Item 15. Controls and Procedures
- Item 16. Reserved
- Item 16A. Audit committee financial expert
- Item 16B. Code of Ethics
- Item 16C. Principal Accountant Fees and Services
- Item 16D. Exemptions from the Listing Standards for Audit Committees
- Item 16E. Purchases of Equity Securities by the Issuer and Affiliated Purchasers
- Item 16F. Change in Registrant's Certifying Accountant
- Item 16G. Corporate Governance
- Item 16H. Mine Safety Disclosure
- Item 16I. Disclosure Regarding Foreign Jurisdictions that Prevent Inspections
- Item 16J. Insider trading policies
- Item 16K. Cybersecurity

**PART III**
- Item 17. Financial Statements
- Item 18. Financial Statements
- Item 19. Exhibits
- Signatures

## 20FR12B

### 20FR12B

**INTRODUCTION AND USE OF CERTAIN TERMS**
**SPECIAL NOTE REGARDING FORWARD-LOOKING STATEMENTS**

**PART I**
- Item 1. Identity of Directors, Senior Management and Advisers
  - 1.A. Directors and Senior Management
  - 1.B. Advisers
  - 1.C. Auditors
- Item 2. Offer Statistics and Expected Timetable
- Item 3. Key Information
  - 3.A. Selected Financial Data
  - 3.B. Capitalization and Indebtedness
  - 3.C. Reasons for the Offer and Use of Proceeds
  - 3.D. Risk Factors
- Item 4. Information on the Company
  - 4.A. History and Development of the Company
  - 4.B. Business Overview
  - 4.C. Organizational Structure
  - 4.D. Property, Plants and Equipment
- Item 5. Operating and Financial Review and Prospects
  - 5.A. Operating Results
  - 5.B. Liquidity and Capital Resources
  - 5.C. Research and Development, Patents and Licenses, etc.
  - 5.D. Trend Information
  - 5.E. Off-Balance Sheet Arrangements
  - 5.F. Tabular Disclosure of Contractual Obligations
- Item 6. Directors, Senior Management and Employees
  - 6.A. Directors and Senior Management
  - 6.B. Compensation
  - 6.C. Board Practices
  - 6.D. Employees
  - 6.E. Share Ownership
- Item 7. Major Shareholders and Related Party Transactions
  - 7.A. Major Shareholders
  - 7.B. Related Party Transactions
  - 7.C. Interests of Experts and Counsel
- Item 8. Financial Information
  - 8.A. Consolidated Statements and Other Financial Information
  - 8.B. Significant Changes
- Item 9. The Offer and Listing
  - 9.A. Listing Details
  - 9.B. Plan of Distribution
  - 9.C. Markets
  - 9.D. Selling Shareholders
  - 9.E. Dilution
  - 9.F. Expenses of the Issue
- Item 10. Additional Information
  - 10.A. Share Capital
  - 10.B. Memorandum and Articles of Association
  - 10.C. Material Contracts
  - 10.D. Exchange Controls
  - 10.E. Taxation
  - 10.F. Dividends and Paying Agents
  - 10.G. Statement by Experts
  - 10.H. Documents on Display
  - 10.I. Subsidiary Information
- Item 11. Quantitative and Qualitative Disclosures About Market Risk
- Item 12. Description of Securities Other than Equity Securities
  - 12.A. Debt Securities
  - 12.B. Warrants and Rights
  - 12.C. Other Securities
  - 12.D. American Depositary Shares

**PART II**
- Item 13. Defaults, Dividend Arrearages and Delinquencies
- Item 14. Material Modifications to the Rights of Security Holders and Use of Proceeds
- Item 15. Controls and Procedures
- Item 16. [Reserved]
  - 16.A. Audit Committee Financial Experts
  - 16.B. Code of Ethics
  - 16.C. Principal Accountant Fees and Services
  - 16.D. Exemptions from the Listing Standards for Audit Committees
  - 16.E. Purchases of Equity Securities by the Issuer and Affiliated Purchasers
  - 16.F. Change in Registrant's Certifying Accountant
  - 16.G. Corporate Governance

**PART III**
- Item 17. Financial Statements
- Item 18. Financial Statements
- Item 19. Exhibits
- Signatures

## 24F-2NT

### 24F-2NT

XML.

## 25

### 25

HTML. We can do something cool here with the checkmark.

## 25-NSE

### 25-NSE

XML.

## 253G1, 253G2, 253G3

### 253G1, 253G2, 253G3

Looks standardizable, can't find docs.

# Insider Trading Disclosures
## 3 

### 3
XML.

## 4
### 4

XML.

## 5
### 5
XML.

## 305B2
### 305B2
Can't find docs.

## 40-17F1, 40-17F2
### 40-17F1, 40-17F2
Doesn't look standardizable

## 40-17G
### 40-17G
Doesn't look standardizable

## 40-17GCS
### 40-17GCS
Doesn't look standardizable

## 40-24B2
### 40-24B2
Doesn't look standardizable

## 40-33
### 40-33
Doesn't look standardizable

## 40-6B
### 40-6B
Can't find docs.

## 40-8B25
### 40-8B25
Can't find docs

## 40-APP
### 40-APP
Cant find docs

## 40-F
Looks standardizable as well as other documents besides root form
## 40FR12B/A
Can't find docs

## 424B1 through 424B8
Can't find docs

## 424H
Can't find docs

## 424I
Neat. Looks like will need a custom parser for exhibit tables.

## 425
Can't standardize - random biz communications.

## 485APOS
can't find docs

## 485BPOS
can't find docs

## 486BXT

### 486BXT
Looks like it's checkboxes again! will be fun.

## 487
cant find docs

## 497
### 497
Can't standardize.

## 497AD
### 497AD
Can't standardize.

## 497J
### 497J
Can't standardize.

## 497K
### 497K
Can't standardize

## 497VPI
### 497VPI
Can't standardize

## 497VPSUB
### 497VPSUB
Can't standardize.

## 497VPU
### 497VPU
Can't standardize.

## 6-K
### 6-K
Can't standardize.

## 8-A12B

### 8-A12B
Item 1. Description of Registrant’s Securities to be Registered.
Item 2. Exhibits.

## 8-A12G
### 8-A12G
Item 1. Description of Registrant’s Securities to be Registered.
Item 2.	Exhibits.
## 8-K

[Instructions](https://www.sec.gov/files/form8-k.pdf)

### 8-K

- Item 1.01. Entry into a Material Definitive Agreement
- Item 1.02. Termination of a Material Definitive Agreement
- Item 1.03. Bankruptcy or Receivership
- Item 1.04. Mine Safety – Reporting of Shutdowns and Patterns of Violations
- Item 1.05. Material Cybersecurity Incidents
- Item 2.01. Completion of Acquisition or Disposition of Assets
- Item 2.02. Results of Operations and Financial Condition
- Item 2.03. Creation of a Direct Financial Obligation or an Obligation under an Off-Balance Sheet Arrangement of a Registrant
- Item 2.04. Triggering Events That Accelerate or Increase a Direct Financial Obligation or an Obligation under an Off-Balance Sheet Arrangement
- Item 2.05. Costs Associated with Exit or Disposal Activities
- Item 2.06. Material Impairments
- Item 3.01. Notice of Delisting or Failure to Satisfy a Continued Listing Rule or Standard; Transfer of Listing
- Item 3.02. Unregistered Sales of Equity Securities
- Item 3.03. Material Modification to Rights of Security Holders
- Item 4.01. Changes in Registrant's Certifying Accountant
- Item 4.02. Non-Reliance on Previously Issued Financial Statements or a Related Audit Report or Completed Interim Review
- Item 5.01. Changes in Control of Registrant
- Item 5.02. Departure of Directors or Certain Officers; Election of Directors; Appointment of Certain Officers; Compensatory Arrangements of Certain Officers
- Item 5.03. Amendments to Articles of Incorporation or Bylaws; Change in Fiscal Year
- Item 5.04. Temporary Suspension of Trading Under Registrant's Employee Benefit Plans
- Item 5.05. Amendments to the Registrant's Code of Ethics, or Waiver of a Provision of the Code of Ethics
- Item 5.06. Change in Shell Company Status
- Item 5.07. Submission of Matters to a Vote of Security Holders
- Item 5.08. Shareholder Director Nominations
- Item 6.01. ABS Informational and Computational Material
- Item 6.02. Change of Servicer or Trustee
- Item 6.03. Change in Credit Enhancement or Other External Support
- Item 6.04. Failure to Make a Required Distribution
- Item 6.05. Securities Act Updating Disclosure
- Item 6.06. Static Pool
- Item 7.01. Regulation FD Disclosure
- Item 8.01. Other Events
- Item 9.01. Financial Statements and Exhibits

## 8-K12B
Pretty sure this is just a specific case of an [8-K](#8-k)
### 8-K12B
[See 8-K](#8-k)

## 8-K12G3
Pretty sure this is just a specific case of an [8-K](#8-k)
### 8-K12G3
[See 8-K](#8-k)

## 8-K15D5
Pretty sure this is just a specific case of an [8-K](#8-k)
### 8-K15D5
[See 8-K](#8-k)

## ABS-15G

[Instructions](https://www.sec.gov/files/formabs-15g.pdf)

### ABS-15G

**Part I:**
- Item 1.01 Initial Filing of Rule 15Ga-1 Representations and Warranties Disclosure
- Item 1.02 Periodic Filing of Rule 15Ga-1 Representations and Warranties Disclosure
- Item 1.03 Notice of Termination of Duty to File Reports under Rule 15Ga-1

**Part II: Findings and Conclusions of Third-Party Due Diligence Reports:**
- Item 2.01 Findings and Conclusions of a Third Party Due Diligence Report Obtained by the Issuer
- Item 2.02 Findings and Conclusions of a Third-Party Due Diligence Report Obtained by the Underwriter

**Signatures**

## ABS-EE
### ABS-EE

### EX-102	
XML.

### EX-103	
XML.

## ANNLRPT
### ANNLRPT
Can't find docs.

## APP NTC

### APP NTC
This has not been implemented yet - need to rejig pdf parser mapping dict to use underline
agency
action
summary
applicants
filing
hearing
addresses
further contact
supplementary information

## APP ORDR

### APP ORDR
After pdf parser rejig, look at this.

## APP WD
### APP WD
Can't standardize.

## APP WDG
### APP WDG
Can standardize, but not sure if need to?

## ARS
### ARS
Can't find docs.

# ATS-N
Come back later.
## ATS-N/CA

## ATS-N/MA

## ATS-N/OFA

## ATS-N/UA

## AW
Huh, looks like it might be interesting to standardize this.
### AW

## AW WD
Huh, looks like it might be interesting to standardize this.
### AW WD

## C
### C
XML.

## C-AR

### C-AR
XML.

## C-TR

### C-TR
XML.

## C-TR-W

### C-TR-W
XML.

## C-U

### C-U
XML.

## C-U-W

### C-U-W
XML.

## C-W

### C-W
XML.

## CB
[Instructions](https://www.sec.gov/files/formcb.pdf)

### CB
PART I - INFORMATION SENT TO SECURITY HOLDERS
Item 1. Home Jurisdiction Documents
Item 2. Informational Legends 
PART II - INFORMATION NOT REQUIRED TO BE SENT TO SECURITY HOLDERS 
PART III - CONSENT TO SERVICE OF PROCESS 
PART IV - SIGNATURES 

## CERT
### CERT
Can't standardize.

## CFPORTAL
### CFPORTAL
XML.

## CFPORTAL-W
### CFPORTAL-W
XML.

## CORRESP
Maybe standardize - same letter format so i think so?

### CORRESP

## CT ORDER
Do not standardize yet. If someone asks.
### CT ORDER

## D
### D
XML

# Proxy Statements
DEF 14C
DEFA14A
DEFA14C
DEFC14A
DEFM14A
DEFM14C
DEFR14A
DFAN14A
DFRN14A
Going to sit on these a bit. I need a valid use case from someone to justify time commitment.

## DEL AM
### DEL AM
Letter format. might standardize.

## DRS
### DRS
Standardization might be possible. DRS contains eg s1, f1 etc.

## DRSLTR
### DRSLTR
Letter format


## AUDITED FINANCIAL STATEMENTS	
Might be possible? https://www.sec.gov/Archives/edgar/data/2044949/000109690625000882/ex_b_audited_financial.pdf

## JOINT FIRM INTENTION ANNOUNCEMENT
https://www.sec.gov/Archives/edgar/data/1921865/000147793225004069/aspi_ex993.htm

## PRESS RELEASE
https://www.sec.gov/Archives/edgar/data/1921865/000147793225004069/aspi_ex994.htm


## SD

[Instructions](https://www.sec.gov/files/formsd.pdf)

### SD

- Item 1.01 Conflict Minerals Disclosure and Report
- Item 1.02 Exhibit
- Item 2.01 Resource Extraction Issuer Disclosure and Report
- Item 3.01 Exhibits

**Signatures**

## IRANNOTICE

N/A.

## NT-10K

For notices look into:
- 2024, NT 10-K, 968
- 2024, NT 10-K/A, 10
- 2024, NT 10-Q, 1664
- 2024, NT 10-Q/A, 15
- 2024, NT 11-K, 18
- 2024, NT 20-F, 187
- 2024, NT 20-F/A, 2
- 2024, NT N-CEN, 18
- 2024, NT N-MFP2, 2
- 2024, NT NPORT-P, 109
- 2024, NT-NCEN, 11
- 2024, NT-NCSR, 22
- 2024, NT-NCSR/A, 8

Should all be the same?

### NT-10K, NT 10-Q, NT 20-F

- Part I — Registrant Information
- Part II — Rules 12b-25(b) and (c)
- Part III — Narrative
- Part IV — Other Information
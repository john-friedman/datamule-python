from datamule import Portfolio, Document
import os 
from time import time
import pandas as pd

# inspect the data
#document = Document(filename='4/01/000199937124001221/galbraith-form4_013124.xml',type='4')


def process_submission(submission):
    doc_list = []
    
    metadata = submission.metadata['submission']
    if 'ACCESSION-NUMBER' in metadata.keys():
        accession_number = metadata['ACCESSION-NUMBER']
        filing_date = metadata['FILING-DATE']
        reporting_date = metadata['PERIOD']
    else:
        accession_number = metadata['ACCESSION NUMBER']
        filing_date = metadata['FILED AS OF DATE']
        reporting_date = metadata['CONFORMED PERIOD OF REPORT']

    for document in submission.document_type(['4']):
        document.parse()
        # Note: we are assuming that the first transaction indicates the type of transaction
        try:
            type = document.data['holdings'][0]['transactionAmounts']['acquiredDisposedCode']['value']
            doc_dict = {
                'accession_number': accession_number,
                'filing_date': filing_date,
                'reporting_date': reporting_date,
                'type': type,
                'issuer_cik': document.data['metadata']['issuer']['cik'],
                }
            

            doc_list.append(doc_dict)
        except:
            pass
    return doc_list

for month in range(1,13):
    portfolio = Portfolio(f"4/{month:02d}")
    submission_results = portfolio.process_submissions(process_submission) 
    results = [doc for sub_docs in submission_results for doc in sub_docs]
    df = pd.DataFrame(results)
    df.to_csv('4.csv', mode='a', header=not os.path.exists('4.csv'), index=False)



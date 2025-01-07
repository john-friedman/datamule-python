from datamule import Portfolio
import os 
import pysentiment2 as ps
from time import time
import pandas as pd
# Load sentiment analyzer
lm = ps.LM()

def process_submission(submission):
    doc_list = []
    try:
        metadata = submission.metadata['submission']
        if 'ACCESSION-NUMBER' in metadata.keys():
            accession_number = metadata['ACCESSION-NUMBER']
            filing_date = metadata['FILING-DATE']
            reporting_date = metadata['PERIOD']
            cik = metadata['FILER']['COMPANY-DATA']['CIK']
            company_name = metadata['FILER']['COMPANY-DATA']['CONFORMED-NAME']
        else:
            accession_number = metadata['ACCESSION NUMBER']
            filing_date = metadata['FILED AS OF DATE']
            reporting_date = metadata['CONFORMED PERIOD OF REPORT'] 
            cik = metadata['FILER']['COMPANY DATA']['CENTRAL INDEX KEY']
            company_name = metadata['FILER']['COMPANY DATA']['COMPANY CONFORMED NAME']

        for document in submission:
            try:
                sentiment = None
                if ((document.path.suffix in ['.txt', '.html', '.htm']) & (document.type not in ['XML'])):
                    document._load_content()
                    tokens = lm.tokenize(document.content)
                    scores = lm.get_score(tokens)
                    sentiment = scores['Polarity']

                doc_dict = {
                    'accession_number': accession_number,
                    'filing_date': filing_date,
                    'cik': cik,
                    'company_name': company_name,
                    'reporting_date': reporting_date,
                    'type': document.type,
                    'sentiment': sentiment
                    }
                doc_list.append(doc_dict)
            except:
                pass

        return doc_list

    except:
        pass
    


for month in range(1,13):
    port_dir = os.listdir(f"8-K/{month:02d}")
    days_dir = [f"8-K/{month:02d}/{day}" for day in port_dir]
    
    for day in days_dir:
        try:
            portfolio = Portfolio(day)
            submission_results = portfolio.process_submissions(process_submission) 
            day_results = [doc for sub_docs in submission_results for doc in sub_docs if doc['sentiment'] is not None]
            df = pd.DataFrame(day_results)
            df.to_csv('8k.csv', mode='a', header=not os.path.exists('8k.csv'), index=False)
            print(f"Finished processing {day}")
        except:
            print(f"Error processing {day}")



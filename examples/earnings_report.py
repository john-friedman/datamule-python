# Download earnings announcements for a given date range and save them to a new folder.

from datamule import Portfolio
from pathlib import Path
import shutil

portfolio = Portfolio('8K')

portfolio.download_submissions(submission_type='8-K',filing_date=('2020-01-01','2020-01-31'))

def process_submission(submission):
    try:
        for document in submission.document_type(['8-K']):
            document.parse()
            
            if 'item2.02' in document.data['document'].keys():
                for document in submission.document_type(['EX-99.1']):
                    return document.path
    except:
        return None
                

paths = portfolio.process_submissions(process_submission)
paths = [p for p in paths if p is not None]

new_folder = Path('earnings_announcements')
new_folder.mkdir(exist_ok=True)

for path in paths:
    new_path = new_folder / path.name
    shutil.copy(path, new_path)  # Copy the file
    

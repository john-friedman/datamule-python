# Streams data rather than downloading it. 
# additional functionality such as query by xbrl, and other db
# also this is basically our experimental rework of portfolio w/o disturbing existing users
# this is highly experimental and may not work as expected
# only for datamule source
# likely new bottleneck will be local parsing() - will be bypassed in future when we have parsed archive
# wow parsed archive is going to be crazy fast - like every 10k in 1 minute.

# example queries filter by sic = 7372, xbrl query = dei:operatingprofit > 0 in date range 2018-2019

# hmm do we go for sql esq or not.
# I think we do.
# i think we remove cik, ticker, sic, etc and just have a query object
# should be sql esq so users can use it easily w/o learnign new syntax

# WHERE submission_type = '10-K'
# AND us-gaap:ResearchAndDevelopmentExpense > 0 
# AND dei:debt_to_equity < 2
# AND filing_date BETWEEN '2023-01-01' AND '2023-12-31'
# AND CIK in (123, 456, 789)
# AND SIC in (123, 456, 789)
# AND ticker in ('AAPL', 'GOOGL', 'AMZN')
# AND document_type = 'EX-99.1' # to select attachments

from .eftsquery import EFTSQuery
from secsgml import parse_sgml_submission_into_memory
from ..helper import load_package_dataset, identifier_to_cik
from datetime import datetime


class Book():
    def __init__(self):
        self.EFTSQuery = EFTSQuery()
    def process_submissions(self,cik=None,ticker=None,sic=None,submission_type=None,document_type=None,filing_date=None,
                            xbrl_query={},
                            search_text=None,
                            search_text_callback=None,
                            xbrl_query_callback=None,
                            metadata_callback=None,
                            document_callback=None,):
        # cleaning
        if ticker is not None:
            cik = identifier_to_cik(ticker)
        else:
            cik = cik

        if cik is not None:
            if isinstance(cik, str):
                cik = [str(cik)]
            else:
                cik = [str(c) for c in cik]

        if sic is not None:
            if isinstance(sic, str):
                sic = [sic]
            else:
                sic = [s for s in sic]

        if submission_type is not None:
            if isinstance(submission_type, str):
                submission_type = [str(submission_type)]
            else:
                submission_type = [str(s) for s in submission_type]

        if document_type is not None:
            if isinstance(document_type, str):
                document_type = [str(document_type)]
            else:
                document_type = [str(d) for d in document_type]

        if filing_date is None:
            filing_date = ("2001-01-01",{datetime.now().strftime('%Y-%m-%d')})

        if isinstance(filing_date, str):
            filing_date = (filing_date,filing_date)
        

        search_text_data = self.EFTSQuery.query_efts(cik=cik, submission_type=submission_type,
                                             filing_date=filing_date, search_text=search_text)
        
        # add search text callback here
        if search_text_callback is not None:
            search_text_data = search_text_callback(search_text_data)


        sics = load_package_dataset('company_metadata')
        sic_matches = [item['cik'] for item in sics if str(item['sic']) in sic]
        search_text_data = [item for item in search_text_data if any(cik in sic_matches for cik in item['ciks'])]

        # filter by xbrl query

        # grab urls and parse them into memory

        # metadata callback

        # document callback
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


class Book():
    def process_submissions(self,cik,ticker,sic,submission_type,document_type,date,
                            xbrl_query={},
                            metadata_callback=None,
                            document_callback=None,):
        # grabs data and processes it
        pass 
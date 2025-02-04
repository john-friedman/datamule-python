# Streams data rather than downloading it. 
# additional functionality such as query by xbrl, and other db
# also this is basically our experimental rework of portfolio w/o disturbing existing users
# this is highly experimental and may not work as expected
# only for datamule source
# likely new bottleneck will be local parsing() - will be bypassed in future when we have parsed archive
# wow parsed archive is going to be crazy fast - like every 10k in 1 minute.

class Book():
    pass
    def process_submissions(self,cik,ticker,sic,submission_type,document_type,date,
                            xbrl_query={},
                            metadata_callback=None,
                            document_callback=None,):
        # grabs data and processes it
        pass 
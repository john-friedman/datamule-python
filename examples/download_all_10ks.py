# INSTALLATION #
# pip install datamule #


from datamule import Portfolio
from datetime import datetime, timedelta
import calendar
from time import sleep

# Specify directory to download files to
output_dir = '10k'

# Your api key. Not needed if you set DATAMULE_API_KEY as an environmental variable.
# See: https://john-friedman.github.io/datamule-python/datamule-python/data_provider/
YOUR_API_KEY = ""

# SET FOR TESTING PURPOSES #
start_year = 2007
current_year = 2007
current_month = 1


# UNCOMMENT TO DOWNLOAD FULL SAMPLE #
# start_year = 1993
# current_year = datetime.now().year
# current_month = datetime.now().month

# Download filings for each month
for year in range(start_year, current_year + 1):
    start_month = 1 if year > start_year else 1
    end_month = 12 if year < current_year else current_month
    
    for month in range(start_month, end_month + 1):
        portfolio = Portfolio(f'{output_dir}/{year}_{month:02d}')

        # SET YOUR API KEY HERE #
        portfolio.set_api_key(YOUR_API_KEY)


        # What filings to download
        submission_types = ['10-K','10-K/A']

        # What documents within filings to download
        document_types = ['10-K','10-K/A']

        # Calculate first and last day of the month
        first_day = f"{year}-{month:02d}-01"
        last_day = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"

        print(f"Downloading filings for {year}-{month:02d}: {first_day} to {last_day}")
        
        portfolio.download_submissions(
            submission_type=submission_types,
            filing_date=(first_day, last_day),
            document_type=[], # Change this to document types to only download 10-K root forms
            provider = 'datamule' # Uses the datamule provider
        )

# The 10-K documents are now downloaded. They are stored in tar form, with many 10-K filings to a tar.
# Tars are used to increase download speed, and reduce I/O from many small files

# Here is how to interact with the documents using datamule
for year in range(start_year, current_year + 1):
    start_month = 1 if year > start_year else 1
    end_month = 12 if year < current_year else current_month
    
    for month in range(start_month, end_month + 1):
        portfolio = Portfolio(f'{output_dir}/{year}_{month:02d}')
        
        # get submission level data such as metadata or XBRL
        for submission in portfolio:
            print(submission.metadata.content) # Shows you the metadata of the submission, e.g. accession number, cik, filing date,...
            input("Press any key to continue")

            # get document level data
            for document in submission:
                # submission.xbrl # get xbrl

                # only select 10-Ks
                if document.type in ['10-K','10-K/A']:
                    # only get data in form html or text - e.g. ADOBE also publishes their 10-K in PDF form.
                    if document.extension in ['.htm','.txt','.html']:
                        print(document.text[0:2000]) # print first 2000 chars of text
                        input("Press any key to continue")
                        # get document content (e.g. for another script)
                        print(document.content[0:100])
                        input("Press any key to continue")
                        # parse using datamule, e.g. if you want items. Also works for company designated headers for html files
                        print(document.data)
                        input("Press any key to continue")

                        # get specific section (may want to wrap in try block)
                        print(document.get_section(title='signatures', format='text'))
                        input("Press any key to continue")

                        # visualize parsed document
                        document.visualize()
                        input("Press any key to continue")


# If you would like to convert them out of tar form, here is a helper function. Warning, it has not been tested at scale.
# Alternatives such as using 7zip en masse is probably faster.
sleep(5)
for year in range(start_year, current_year + 1):
    start_month = 1 if year > start_year else 1
    end_month = 12 if year < current_year else current_month
    
    for month in range(start_month, end_month + 1):
        portfolio = Portfolio(f'{output_dir}/{year}_{month:02d}')
        portfolio.decompress()


# NOTE # 
# Downloads may miss a few files. For example, if you download every filing in the corpus, a few hundred or so might be skipped
# To fix this, run the download code a second time. it will only download filings you have missed.
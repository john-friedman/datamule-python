# Example created after Muhsin Tcheifa emailed me a question
# Which made me realize that submissions should be able to load directly from url.
# So now they can.
# Thank you Mr. Tcheifa


from datamule import Portfolio, Submission, format_accession
port = Portfolio('websockettest')

def data_callback(hits):
    for hit in hits:
        cik = hit['ciks'][0]
        accession = hit['accession']
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{format_accession(accession,'dash')}/"
        print(f"Direct URL: {url}")

        # If you want to process this into a Submission()
        sub = Submission(url=url)
        # print what documents are in the submission
        print(sub.metadata.content['documents'])
        # print first 100 chars of a document 
        print(sub.documents[0].content[0:10])

port.stream_submissions(data_callback=data_callback)

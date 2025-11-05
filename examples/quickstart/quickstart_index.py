from datamule import Index
# Search for "risk factors" in Apple's 10-K filings
index = Index()
results = index.search_submissions(
    text_query='"risk factors"',
    submission_type="10-K",
    ticker="AAPL",
)
print(results)
input("Submissions that contain risk factors")

# Search for "war" but exclude "peace" in 10-K filings from January 2023
results = index.search_submissions(
    text_query='war NOT peace',
    submission_type="10-K",
    filing_date=("2023-01-01","2023-01-31"),
    quiet=False,
    requests_per_second=3
)
print(results)
input("Submissions that contain war but not peace")
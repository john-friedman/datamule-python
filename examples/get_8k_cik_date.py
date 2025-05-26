from datamule import Index
import pandas as pd
index = Index()
results = index.search_submissions(
    text_query = None,
    submission_type="8-K",
    filing_date = ('2020-01-01','2020-01-07'),
    quiet = False
)
print(results[0])
rows = [{'cik':item['_source']['ciks'],'file_date':item['_source']['file_date']}  for item in results]
df = pd.DataFrame(rows)
print(df.head())
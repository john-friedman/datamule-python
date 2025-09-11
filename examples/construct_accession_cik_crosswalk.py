from datamule import construct_submissions_data

# CODE TO CONSTRUCT ACCESSIONS CIK CROSSWALK

construct_submissions_data(output_path='accession_cik_crosswalk.csv',columns=['accessionNumber', 'filingDate', 'form',
                                                                              'reportDate'])

import pandas as pd

# Fix 1: Use pd.read_csv() to read the CSV file
df = pd.read_csv('accession_cik_crosswalk.csv')

# Fix 2: Use .isin() method with a list for filtering
df = df[df['submissionType'].isin(['10-K', '10-K/A'])]

# Save the filtered dataframe
df.to_csv('10k_accession_cik_crosswalk.csv', index=False)

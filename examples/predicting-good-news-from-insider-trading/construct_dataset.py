from tqdm import tqdm
import pandas as pd
import numpy as np

from tqdm import tqdm
import pandas as pd
import numpy as np

def process_data(form8k, form4, weeks=8, by_week=True):
   f8k = form8k[abs(form8k['sentiment']) < 0.9].copy()
   f8k = form8k.groupby(['accession_number', 'filing_date', 'cik', 'reporting_date'])['sentiment'].mean().reset_index()
   
   # Convert YYYYMMDD to datetime
   f8k['reporting_date'] = pd.to_datetime(f8k['reporting_date'].astype(str), format='%Y%m%d')
   form4['reporting_date'] = pd.to_datetime(form4['reporting_date'].astype(str), format='%Y%m%d')
   
   clean_8ks = []
   for _, row in tqdm(f8k.iterrows(), total=len(f8k)):
       window = pd.Timedelta(weeks=weeks)
       mask = ((f8k['reporting_date'] - row['reporting_date']).abs() <= window) & (f8k['cik'] == row['cik'])
       if mask.sum() == 1:
           clean_8ks.append(row)
   
   clean_8ks = pd.DataFrame(clean_8ks)
   print(f"Clean 8ks: {len(clean_8ks)}")
   
   results = []
   time_delta = pd.Timedelta(weeks=1) if by_week else pd.Timedelta(days=1)
   periods = weeks if by_week else weeks * 7
   
   for _, event in tqdm(clean_8ks.iterrows(), total=len(clean_8ks)):
       for period in range(-periods, periods+1):
           period_start = event['reporting_date'] + period * time_delta
           period_end = period_start + time_delta
           
           mask = (form4['reporting_date'] >= period_start) & \
                  (form4['reporting_date'] < period_end) & \
                  (form4['issuer_cik'] == event['cik'])
           
           trades = form4[mask]
           results.append({
               'event_id': event['accession_number'],
               'period': period,
               'buys': (trades['type'] == 'A').sum(),
               'sells': (trades['type'] == 'D').sum(),
               'sentiment': event['sentiment']
           })
   
   return pd.DataFrame(results)

# Usage:
form8k_df = pd.read_csv('8k.csv')
form4_df = pd.read_csv('4.csv')

result = process_data(form8k_df, form4_df)
result.to_csv('dataset.csv', index=False)
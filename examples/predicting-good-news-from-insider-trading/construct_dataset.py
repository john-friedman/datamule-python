from tqdm import tqdm
import pandas as pd
import numpy as np

from datamule import load_package_dataset

company_metadata = load_package_dataset('company_metadata')
company_metadata = pd.DataFrame(company_metadata)
company_metadata['cik'] = company_metadata['cik'].astype(int)
# drop duplicates
company_metadata = company_metadata.drop_duplicates(subset='cik')

def process_data(form8k, form4, weeks=8, by_week=True):
   form4['issuer_cik'] = form4['issuer_cik'].astype(int)

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
   clean_8ks['cik'] = clean_8ks['cik'].astype(int)
   clean_8ks = clean_8ks.merge(
       company_metadata[['cik', 'sic']], 
       on='cik', 
       how='left'
   )
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
               'sentiment': event['sentiment'],
               'sic': event['sic']
           })
   
   return pd.DataFrame(results)

# Usage:
form8k_df = pd.read_csv('8k.csv')
form4_df = pd.read_csv('4.csv')

result = process_data(form8k_df, form4_df)

# lets add sic groups
sic_groups = {
    # Agriculture, Forestry, and Fishing
    "Agriculture & Natural Resources": [100, 200, 700, 900, 1000, 1040, 1090, 1220],
    
    # Mining and Oil Extraction
    "Mining & Oil": [1311, 1381, 1382, 1389, 1400, 1520, 1531, 1600, 1623, 1700, 1731],
    
    # Food and Kindred Products
    "Food Processing": [2011, 2013, 2015, 2020, 2024, 2030, 2033, 2040, 2060, 2070, 2080, 2082, 2086, 2090],
    
    # Manufacturing - Basic Materials
    "Basic Materials Manufacturing": [2100, 2111, 2200, 2211, 2300, 2320, 2330, 2400, 2430, 2451],
    
    # Manufacturing - Wood & Paper
    "Wood & Paper Products": [2510, 2511, 2520, 2522, 2531, 2650, 2670, 2673],
    
    # Manufacturing - Chemicals & Allied Products
    "Chemical Manufacturing": [2800, 2810, 2820, 2821, 2833, 2834, 2835, 2836, 2840, 2844, 2851, 2860, 2870, 2890, 2891, 2911, 2990],
    
    # Manufacturing - Industrial & Commercial
    "Industrial Manufacturing": [3011, 3021, 3050, 3060, 3080, 3086, 3089, 3100, 3140, 3211, 3231, 3241, 3260, 3272],
    
    # Manufacturing - Metal Products
    "Metal Products": [3310, 3312, 3317, 3330, 3334, 3350, 3357, 3360, 3390, 3411, 3420, 3430, 3440, 3442, 3443, 3460, 3470, 3480, 3490],
    
    # Manufacturing - Machinery & Equipment
    "Machinery & Equipment": [3510, 3523, 3524, 3530, 3531, 3533, 3540, 3550, 3559, 3560, 3561, 3562, 3564, 3569, 3571, 3572, 3576, 3577, 3578, 3580, 3585, 3590],
    
    # Manufacturing - Electronics
    "Electronics Manufacturing": [3600, 3612, 3613, 3620, 3621, 3630, 3634, 3640, 3651, 3652, 3661, 3663, 3669, 3670, 3672, 3674, 3678, 3679, 3690],
    
    # Manufacturing - Transportation Equipment
    "Transportation Equipment": [3711, 3713, 3714, 3716, 3720, 3721, 3724, 3728, 3730, 3743, 3751, 3760, 3790],
    
    # Manufacturing - Precision Instruments
    "Precision Instruments": [3812, 3823, 3824, 3825, 3826, 3827, 3829, 3841, 3842, 3843, 3844, 3845, 3851, 3861, 3873],
    
    # Manufacturing - Miscellaneous
    "Miscellaneous Manufacturing": [3910, 3944, 3949, 3990],
    
    # Transportation & Public Utilities
    "Transportation & Utilities": [4011, 4210, 4213, 4220, 4400, 4412, 4512, 4513, 4522, 4581, 4610, 4700, 4731],
    
    # Communications
    "Communications": [4812, 4813, 4822, 4832, 4833, 4841, 4899],
    
    # Utilities
    "Utilities & Energy": [4900, 4911, 4922, 4923, 4924, 4931, 4932, 4941, 4953, 4955, 4991],
    
    # Wholesale Trade
    "Wholesale Trade": [5000, 5013, 5030, 5031, 5040, 5045, 5047, 5050, 5051, 5065, 5070, 5080, 5084, 5090, 5094, 5099, 5122, 5130, 5140, 5141, 5150, 5160, 5171, 5172, 5190],
    
    # Retail Trade
    "Retail Trade": [5200, 5211, 5311, 5331, 5400, 5411, 5412, 5500, 5531, 5600, 5621, 5651, 5661, 5700, 5712, 5731, 5734, 5810, 5812, 5900, 5912, 5940, 5961, 5990],
    
    # Finance
    "Finance & Banking": [6021, 6022, 6035, 6036, 6099, 6141, 6153, 6159, 6162, 6163, 6189, 6199, 6200, 6211, 6221, 6282],
    
    # Insurance
    "Insurance": [6311, 6321, 6324, 6331, 6351, 6361, 6411],
    
    # Real Estate
    "Real Estate": [6500, 6510, 6512, 6513, 6519, 6531, 6552, 6770, 6792, 6794, 6795, 6798, 6799],
    
    # Services
    "Business Services": [7011, 7200, 7310, 7311, 7320, 7331, 7340, 7350, 7359, 7361, 7370, 7371, 7372, 7373, 7374, 7380, 7381, 7389],
    
    # Entertainment & Recreation
    "Entertainment": [7500, 7510, 7812, 7819, 7822, 7830, 7841, 7900, 7948, 7990, 7997],
    
    # Healthcare
    "Healthcare": [8000, 8011, 8050, 8051, 8060, 8062, 8071, 8082, 8090, 8093],
    
    # Professional Services
    "Professional Services": [8111, 8200, 8700, 8711, 8731, 8734, 8741, 8742, 8900],
    
    # Other
    "Other": [0] # Unclassified establishments
}

# Create a new column with the SIC group
result['sic_group'] = np.nan
for group, sic_codes in sic_groups.items():
    mask = result['sic'].isin(sic_codes)
    result.loc[mask, 'sic_group'] = group

result.to_csv('dataset.csv', index=False)
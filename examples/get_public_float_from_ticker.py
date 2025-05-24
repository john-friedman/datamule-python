from datamule import Sheet
import pandas as pd


# Download the data
sheet = Sheet('public_float_from_ticker')
sheet.download_xbrl(ticker='MSFT')

# Get the public float value from the downloaded XBRL
import pandas as pd
df = pd.read_csv(r'public_float_from_ticker\789019.csv')


public_float = df.loc[(df['namespace'] == 'dei') & (df['concept_name'] == 'EntityPublicFloat'), 'value']
print(public_float)
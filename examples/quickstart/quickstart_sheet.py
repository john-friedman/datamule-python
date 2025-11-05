# Will be reworked in the enterprise update

from datamule import Sheet
import pandas as pd

sheet = Sheet('sheet_demo')

print(pd.DataFrame(sheet.get_table('accession_cik', ticker=['F'])))
input("All of Ford's Accession Numbers")

print(pd.DataFrame(sheet.get_table('simple_xbrl', taxonomy="us-gaap", 
                                name="NetIncomeLoss", ticker=['META'])))

input("All of META's NetIncomeLoss statements")

print(pd.DataFrame(sheet.get_table('proxy_voting_record', 
                              meetingDate=('2023-01-01', '2023-01-31'))))

input("Proxy Votes that occured in January 2023")

print(pd.DataFrame(sheet.get_table('information_table', cusip='25809K105',filingDate=('2024-01-01', '2024-01-03'))))
print("Institutions that hold Doordash's stock")


print(pd.DataFrame(sheet.get_table('non_derivative_transaction_ownership', 
                                    ticker=['TSLA'], 
                                    transactionDate=('2024-01-01', '2024-03-31'))))
input("Nonderivative Insider trading transactions for Tesla")
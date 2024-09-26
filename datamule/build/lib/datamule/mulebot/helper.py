# TODO custom parse company concepts that feeds descriptions into chatbot
# so we need 1 request from server
# 2. parse all
# 3. have search function that feeds labels into chatbot
# 4. output table

import requests
from datamule.sec_parser import parse_company_concepts
from datamule.global_vars import headers
from datamule.helper import identifier_to_cik

def get_company_concept(ticker):

    cik = identifier_to_cik(ticker)[0]
    url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json'
    response = requests.get(url,headers=headers)
    data = response.json()

    table_dict_list = parse_company_concepts(data)
    print(table_dict_list)

    # drop tables where label is None
    table_dict_list = [table_dict for table_dict in table_dict_list if table_dict['label'] is not None]
    
    return table_dict_list


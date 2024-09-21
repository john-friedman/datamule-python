# TODO custom parse company concepts that feeds descriptions into chatbot
# so we need 1 request from server
# 2. parse all
# 3. have search function that feeds labels into chatbot
# 4. output table

import requests
from datamule.parsers import parse_company_concepts
from datamule.global_vars import headers
from .search import fuzzy_search

def get_company_concept(cik,search_term):
    url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json'
    response = requests.get(url,headers=headers)
    data = response.json()

    table_dict_list = parse_company_concepts(data)

    # drop tables where label is None
    table_dict_list = [table_dict for table_dict in table_dict_list if table_dict['label'] is not None]

    # convert search term to lowercase
    search_term = search_term.lower()

    # convert table labels to lowercase using list comprehension
    labels = [table_dict['label'].lower() for table_dict in table_dict_list]

    # search by label
    matches = fuzzy_search(search_term, labels)
    
    # return matched tables
    matched_tables = [table_dict_list[labels.index(match)] for match in matches]
    
    return matched_tables


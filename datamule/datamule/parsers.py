import requests
from .global_vars import headers

def get_all_company_facts(cik):
    """Get all company facts for a given CIK. Returns a list of dictionaries with information about each fact and the table."""
    url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json'
    response = requests.get(url, headers=headers)

    # Raise an exception if the response code is not 200
    response.raise_for_status()

    # Get the JSON response
    data = response.json()

    # get categories
    categories = list(data['facts'].keys())

    table_dict_list = []
    for category in categories:
        for fact in data['facts'][category]:
            label = data['facts'][category][fact]['label']
            description = data['facts'][category][fact]['description']
            units = list(data['facts'][category][fact]['units'].keys())

            for unit in units:
                table = data['facts'][category][fact]['units'][unit]

                table_dict = {'category': category, 'fact': fact, 'label': label, 'description': description, 'unit': unit, 'table': table}
                table_dict_list.append(table_dict)

    return table_dict_list
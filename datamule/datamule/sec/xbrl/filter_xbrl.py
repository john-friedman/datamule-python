# simple implementation
import requests
from ..utils import headers

def fetch_frame(taxonomy, concept, unit, period):
    url = f"https://data.sec.gov/api/xbrl/frames/{taxonomy}/{concept}/{unit}/{period}.json"
    response = requests.get(url, headers=headers)
    return response.json()


def filter_xbrl(taxonomy, concept, unit, period, logic, value):
    response_data = fetch_frame(taxonomy, concept, unit, period)
    
    if response_data is None:
        raise ValueError("Unable to fetch XBRL data. Incorrect parameters?")
    
    # input validation
    value = int(value)
    
    # Filter data based on logic and value
    data= response_data['data']

    if logic == '>':
        return [row['accn'] for row in data if row['val'] > value]
    elif logic == '<':
        return [row['accn'] for row in data if row['val'] < value]
    elif logic == '>=':
        return [row['accn'] for row in data if row['val'] >= value]
    elif logic == '<=':
        return [row['accn'] for row in data if row['val'] <= value]
    elif logic == '==':
        return [row['accn'] for row in data if row['val'] == value]
    elif logic == '!=':
        return [row['accn'] for row in data if row['val'] != value]
    else:
        raise ValueError(f"Invalid logic operator: {logic}")


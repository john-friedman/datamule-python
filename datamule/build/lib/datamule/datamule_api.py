import requests

def parse_textual_filing(url,return_type):
    if return_type not in ['simplify','interactive','json']:
        raise ValueError('return_type must be one of "simplify","interactive","json"')
    base_url = 'https://jgfriedman99.pythonanywhere.com/parse_url'
    params = {'url':url,'return_type':return_type}
    response = requests.get(base_url,params=params)
    if response.status_code != 200:
        raise ValueError('Server error')
    
    if return_type == 'simplify':
        # return as html
        return response.text
    elif return_type == 'interactive':
        # return as html
        return response.text
    elif return_type == 'json':
        # return as dict
        return response.json()
    

from .utils import _flatten_dict
# we will need to check if keys exist

def process_24f_2nt(parsed_data):
    annual_filings_info = parsed_data['edgarSubmission']['formData']['annualFilings']['annualFilingInfo'].pop()
    
def process_144(parsed_data):
    data = parsed_data['edgarSubmission']

    if 'headerData' in data:
        header_data = data['headerData']

    if 'formData' in data:
        form_data = data['formData']

def process_proxy_voting_record(parsed_data):
    data = parsed_data['proxyVoteTable']['proxyTable']

def process_npx(parsed_data):
    data = parsed_data['edgarSubmission']

def process_information_table(parsed_data):
    data = parsed_data['informationTable']['infoTable']

def process_13f(parsed_data):
    data = parsed_data['edgarSubmission']
    if "infoTable" in data:
        info_table = data['infoTable']

def process_sbsef(parsed_data):
    data = parsed_data['edgarSubmission']


def process_345(parsed_data):
    data = parsed_data['ownershipDocument']

    if "derivativeTable" in data:
        derivative_table = data['derivativeTable']

        if "derivativeTransaction" in derivative_table:
            if isinstance(derivative_table['derivativeTransaction'], list):
                derivative_transaction = derivative_table['derivativeTransaction'].pop()
            else:
                derivative_transaction = derivative_table.pop('derivativeTransaction')

        if "derivativeHolding" in derivative_table:
            if isinstance(derivative_table['derivativeHolding'], list):
                derivative_holding = derivative_table['derivativeHolding'].pop()
            else:
                derivative_holding = derivative_table.pop('derivativeHolding')

    if "nonDerivativeTable" in data:
        non_derivative_table = data['nonDerivativeTable']

        if "nonDerivativeTransaction" in non_derivative_table:
            if isinstance(non_derivative_table['nonDerivativeTransaction'], list):
                non_derivative_transaction = non_derivative_table['nonDerivativeTransaction'].pop()
            else:
                non_derivative_transaction = non_derivative_table.pop('nonDerivativeTransaction')

        if "nonDerivativeHolding" in non_derivative_table:
            if isinstance(non_derivative_table['nonDerivativeHolding'], list):
                non_derivative_holding = non_derivative_table['nonDerivativeHolding'].pop()
            else:
                non_derivative_holding = non_derivative_table.pop('nonDerivativeHolding')

    # process metadata


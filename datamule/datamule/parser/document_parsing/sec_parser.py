import xml.etree.ElementTree as ET


class Parser:

    def __init__(self):
        pass

    def parse_filing(self, filename, filing_type):
        if filing_type == 'INFORMATION TABLE':
            return parse_13f_hr_information_table_xml(filename)
        elif filing_type == '8-K':
            return parse_8k(filename)
        elif filing_type == '10-K':
            return parse_10k(filename)
        elif filing_type == '10-Q':
            return parse_10q(filename)
        elif filing_type in ['3', '4', '5']:
            return parse_form345(filename)
        elif filing_type == 'D':
            return parse_form_d(filename)
        elif filing_type == 'NPORT-P':
            return parse_nport_p(filename)
        elif filing_type == 'SC 13D':
            return parse_13d(filename)
        elif filing_type == 'SC 13G':
            return parse_13g(filename)
        else:
            raise ValueError(f'Filing type {filing_type} not supported')


    def parse_company_concepts(self, data):
    
        # get cik
        cik = data['cik']
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

                    # Find all unique keys across all rows
                    all_keys = set()
                    for row in table:
                        all_keys.update(row.keys())

                    # Ensure all rows have all keys
                    for row in table:
                        for key in all_keys:
                            if key not in row:
                                row[key] = None

                    table_dict = {'cik':cik, 'category': category, 'fact': fact, 'label': label, 'description': description, 'unit': unit, 'table': table}
                    table_dict_list.append(table_dict)

        return table_dict_list
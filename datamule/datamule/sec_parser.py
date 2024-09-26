
class Parser:
    def __init__(self):
        pass

    # WIP. will setup after parse filing API is updated to send to json first.
    def parse_filing(arg):
        # add handling for url vs file
        pass

    # WIP
    def parse_company_concepts(data):
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

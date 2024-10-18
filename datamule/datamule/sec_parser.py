import xml.etree.ElementTree as ET
from .datamule_api import parse_textual_filing

class Parser:
    def __init__(self):
        pass

    def parse_filing(self, file, filing_type):
        # add handling for url vs file
        # api will handle filing type detection
        if filing_type == '13F-HR-INFORMATIONTABLE':
            return self._parse_13f_hr_information_table_xml(file)
        else:
            data = parse_textual_filing(url=file, return_type='json')
        return data 

    def _parse_13f_hr_information_table_xml(self, xml_file):
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()

        data = []
        
        # Iterate through each infoTable
        for info_table in root.findall('.//{*}infoTable'):
            row = {
                'NAME_OF_ISSUER': info_table.findtext('.//{*}nameOfIssuer') or '',
                'TITLE_OF_CLASS': info_table.findtext('.//{*}titleOfClass') or '',
                'CUSIP': info_table.findtext('.//{*}cusip') or '',
                'FIGI': info_table.findtext('.//{*}figi') or '',
                'VALUE_IN_DOLLARS': info_table.findtext('.//{*}value') or '',
                'SHARES_OR_PRINCIPAL_AMOUNT': '',
                'SHARES_OR_PRINCIPAL_AMOUNT_TYPE': '',
                'PUT_OR_CALL': info_table.findtext('.//{*}putCall') or '',
                'INVESTMENT_DISCRETION': info_table.findtext('.//{*}investmentDiscretion') or '',
                'OTHER_MANAGER': info_table.findtext('.//{*}otherManager') or '',
                'VOTING_AUTHORITY_SOLE': '',
                'VOTING_AUTHORITY_SHARED': '',
                'VOTING_AUTHORITY_NONE': ''
            }
            
            shrs_or_prn_amt = info_table.find('.//{*}shrsOrPrnAmt')
            if shrs_or_prn_amt is not None:
                row['SHARES_OR_PRINCIPAL_AMOUNT'] = shrs_or_prn_amt.findtext('.//{*}sshPrnamt') or ''
                row['SHARES_OR_PRINCIPAL_AMOUNT_TYPE'] = shrs_or_prn_amt.findtext('.//{*}sshPrnamtType') or ''
            
            voting_authority = info_table.find('.//{*}votingAuthority')
            if voting_authority is not None:
                row['VOTING_AUTHORITY_SOLE'] = voting_authority.findtext('.//{*}Sole') or ''
                row['VOTING_AUTHORITY_SHARED'] = voting_authority.findtext('.//{*}Shared') or ''
                row['VOTING_AUTHORITY_NONE'] = voting_authority.findtext('.//{*}None') or ''
            
            data.append(row)

        return data

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
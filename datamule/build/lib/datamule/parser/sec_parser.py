import xml.etree.ElementTree as ET
from ..datamule_api import parse_textual_filing
from .basic_8k_parser import parse_8k
from .basic_10k_parser import parse_10k
from .basic_10q_parser import parse_10q

class Parser:

    def __init__(self):
        pass

    def parse_filing(self, filename, filing_type):
        # add handling for url vs file
        # api will handle filing type detection
        if filing_type == '13F-HR-INFORMATIONTABLE':
            return self._parse_13f_hr_information_table_xml(filename)
        elif filing_type == '8-K':
            return parse_8k(filename)
        elif filing_type == '10-K':
            return parse_10k(filename)
        elif filing_type == '10-Q':
            return parse_10q(filename)
        else:
            data = parse_textual_filing(url=filename, return_type='json')
        return data 

    def _parse_13f_hr_information_table_xml(self, xml_file):
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()

        data = []
        
        # Iterate through each infoTable
        for info_table in root.findall('.//{*}infoTable'):
            row = {
                'NAMEOFISSUER': info_table.findtext('.//{*}nameOfIssuer') or '',
                'TITLEOFCLASS': info_table.findtext('.//{*}titleOfClass') or '',
                'CUSIP': info_table.findtext('.//{*}cusip') or '',
                'FIGI': info_table.findtext('.//{*}figi') or '',
                'VALUE': info_table.findtext('.//{*}value') or '',
                'SSHPRNAMT': '',
                'SSHPRNAMTTYPE': '',
                'PUTCALL': info_table.findtext('.//{*}putCall') or '',
                'INVESTMENTDISCRETION': info_table.findtext('.//{*}investmentDiscretion') or '',
                'OTHERMANAGER': info_table.findtext('.//{*}otherManager') or '',
                'VOTING_AUTH_SOLE': '',
                'VOTING_AUTH_SHARED': '',
                'VOTING_AUTH_NONE': ''
            }
            
            shrs_or_prn_amt = info_table.find('.//{*}shrsOrPrnAmt')
            if shrs_or_prn_amt is not None:
                row['SSHPRNAMT'] = shrs_or_prn_amt.findtext('.//{*}sshPrnamt') or ''
                row['SSHPRNAMTTYPE'] = shrs_or_prn_amt.findtext('.//{*}sshPrnamtType') or ''
            
            voting_authority = info_table.find('.//{*}votingAuthority')
            if voting_authority is not None:
                row['VOTING_AUTH_SOLE'] = voting_authority.findtext('.//{*}Sole') or ''
                row['VOTING_AUTH_SHARED'] = voting_authority.findtext('.//{*}Shared') or ''
                row['VOTING_AUTH_NONE'] = voting_authority.findtext('.//{*}None') or ''
            
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
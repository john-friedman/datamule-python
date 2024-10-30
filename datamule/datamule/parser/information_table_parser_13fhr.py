from xml.etree import ElementTree as ET

def parse_13f_hr_information_table_xml(xml_file):
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


import xml.etree.ElementTree as ET
import csv

from ..tables.tables_informationtable import information_table_dict

def construct_filing(input_file, output_file):
    pass

def construct_document(input_file, output_file, document_type):
    document_type = document_type.lower()
    if document_type == 'information table':
        construct_information_table(input_file, output_file)

def construct_information_table(input_file, output_file):
    # Create root element with namespaces
    root = ET.Element('informationTable')
    root.set('xmlns', 'http://www.sec.gov/edgar/document/thirteenf/informationtable')
    root.set('xmlns:ns2', 'http://www.sec.gov/edgar/common')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xsi:schemaLocation', 
             'http://www.sec.gov/edgar/document/thirteenf/informationtable eis_13FDocument.xsd')
    
    # Read CSV and create infoTable elements
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            info_table = ET.SubElement(root, 'infoTable')
            
            # Add simple elements in order
            if row.get('nameOfIssuer'):
                ET.SubElement(info_table, 'nameOfIssuer').text = row['nameOfIssuer']
            
            if row.get('titleOfClass'):
                ET.SubElement(info_table, 'titleOfClass').text = row['titleOfClass']
            
            if row.get('cusip'):
                ET.SubElement(info_table, 'cusip').text = row['cusip']
            
            if row.get('value'):
                ET.SubElement(info_table, 'value').text = row['value']
            
            # Handle shrsOrPrnAmt nested structure
            if row.get('sharesOrPrincipalAmount') or row.get('sharesOrPrincipalAmountType'):
                shrs_or_prn_amt = ET.SubElement(info_table, 'shrsOrPrnAmt')
                
                if row.get('sharesOrPrincipalAmount'):
                    ET.SubElement(shrs_or_prn_amt, 'sshPrnamt').text = row['sharesOrPrincipalAmount']
                
                if row.get('sharesOrPrincipalAmountType'):
                    ET.SubElement(shrs_or_prn_amt, 'sshPrnamtType').text = row['sharesOrPrincipalAmountType']
            
            if row.get('investmentDiscretion'):
                ET.SubElement(info_table, 'investmentDiscretion').text = row['investmentDiscretion']
            
            # Add otherManager if present
            if row.get('otherManager'):
                ET.SubElement(info_table, 'otherManager').text = row['otherManager']
            
            # Handle votingAuthority nested structure
            if row.get('votingAuthoritySole') or row.get('votingAuthorityShared') or row.get('votingAuthorityNone'):
                voting_authority = ET.SubElement(info_table, 'votingAuthority')
                
                if row.get('votingAuthoritySole'):
                    ET.SubElement(voting_authority, 'Sole').text = row['votingAuthoritySole']
                
                if row.get('votingAuthorityShared'):
                    ET.SubElement(voting_authority, 'Shared').text = row['votingAuthorityShared']
                
                if row.get('votingAuthorityNone'):
                    ET.SubElement(voting_authority, 'None').text = row['votingAuthorityNone']
            
            # Add putCall if present and not empty
            if row.get('putCall') and row['putCall'].strip():
                ET.SubElement(info_table, 'putCall').text = row['putCall']
    
    # Create tree and write with pretty formatting
    tree = ET.ElementTree(root)
    ET.indent(tree, space='\t')  # Use tabs like the original
    
    # Write XML with declaration and stylesheet
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        f.write("<?xml-stylesheet type='text/xsl' href=\"INFO-TABLE_X01.xsl\"?>\n")
        tree.write(f, encoding='unicode', xml_declaration=False)
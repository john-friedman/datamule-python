import xml.etree.ElementTree as ET
from ..datamule_api import parse_textual_filing

class Parser:
    """
    A parser class for handling different types of SEC filings and associated data.
    """

    def __init__(self):
        """Initialize a new Parser instance."""
        pass

    def parse_filing(self, file, filing_type):
        """
        Parse an SEC filing based on the specified filing type.

        Parameters
        ----------
        file : str
            Path to the file or URL containing the filing
        filing_type : str
            Type of the SEC filing to parse

        Returns
        -------
        list or dict
            Parsed filing data. Returns a list of dictionaries for 13F-HR tables,
            or a dictionary for other filing types.

        Examples
        --------
        >>> parser = Parser()
        >>> data = parser.parse_filing('path/to/filing.xml', '13F-HR-INFORMATIONTABLE')
        """
        # add handling for url vs file
        # api will handle filing type detection
        if filing_type == '13F-HR-INFORMATIONTABLE':
            return self._parse_13f_hr_information_table_xml(file)
        else:
            data = parse_textual_filing(url=file, return_type='json')
        return data 

    def _parse_13f_hr_information_table_xml(self, xml_file):
        """
        Parse a 13F-HR information table XML file.

        Parameters
        ----------
        xml_file : str
            Path to the XML file containing 13F-HR information table

        Returns
        -------
        list
            List of dictionaries containing parsed information with keys:
            
            - NAMEOFISSUER: Name of the security issuer
            - TITLEOFCLASS: Title/class of the security
            - CUSIP: CUSIP identifier
            - FIGI: FIGI identifier
            - VALUE: Reported value
            - SSHPRNAMT: Shares/principal amount
            - SSHPRNAMTTYPE: Type of shares/principal amount
            - PUTCALL: Put/call indicator
            - INVESTMENTDISCRETION: Investment discretion code
            - OTHERMANAGER: Other manager identifier
            - VOTING_AUTH_SOLE: Sole voting authority
            - VOTING_AUTH_SHARED: Shared voting authority
            - VOTING_AUTH_NONE: No voting authority

        Notes
        -----
        Uses namespace-aware XML parsing with wildcard namespace matching ({*}).
        Empty or missing values are defaulted to empty strings.
        """
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
        """
        Parse company concepts data from SEC filings.

        Parameters
        ----------
        data : dict
            Dictionary containing company concepts data with required keys:
            'cik', 'facts'

        Returns
        -------
        list
            List of dictionaries containing parsed concept data. Each dictionary contains:
            
            - cik: Company's CIK number
            - category: Concept category
            - fact: Fact name
            - label: Fact label
            - description: Fact description
            - unit: Unit of measurement
            - table: Detailed data table

        Notes
        -----
        Handles missing keys in the input data by setting them to None in the output.
        """
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
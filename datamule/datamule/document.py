import json
import csv
import re
from doc2dict import xml2dict, txt2dict, dict2dict
from doc2dict.mapping import flatten_hierarchy
from .mapping_dicts.txt_mapping_dicts import dict_10k, dict_10q, dict_8k, dict_13d, dict_13g
from .mapping_dicts.xml_mapping_dicts import dict_345
from selectolax.parser import HTMLParser

class Document:
    def __init__(self, type, content, extension,accession,filing_date):
        
        self.type = type
        extension = extension.lower()
        self.accession = accession
        self.filing_date = filing_date
        self.content = content
        
        if extension == '.txt':
            self.content = self._preprocess_txt_content()
        elif extension in ['.htm', '.html']:
            self.content = self._preprocess_html_content()

        self.extension = extension
        # this will be filled by parsed
        self.data = None

    #_load_text_content
    def _preprocess_txt_content(self):
            return self.content.read().translate(str.maketrans({
                '\xa0': ' ', '\u2003': ' ',
                '\u2018': "'", '\u2019': "'",
                '\u201c': '"', '\u201d': '"'
            }))

    # will deprecate this when we add html2dict
    def _preprocess_html_content(self):
        parser = HTMLParser(self.content,detect_encoding=True,decode_errors='ignore')
    
        # Remove hidden elements first
        hidden_nodes = parser.css('[style*="display: none"], [style*="display:none"], .hidden, .hide, .d-none')
        for node in hidden_nodes:
            node.decompose()
        
        blocks = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section', 'li', 'td'}
        lines = []
        current_line = []
        
        def flush_line():
            if current_line:
                # Don't add spaces between adjacent spans
                lines.append(''.join(current_line))
                current_line.clear()
        
        for node in parser.root.traverse(include_text=True):
            if node.tag in ('script', 'style', 'css'):
                continue
                
            if node.tag in blocks:
                flush_line()
                lines.append('')
                
            if node.text_content:
                text = node.text_content.strip()
                if text:
                    if node.tag in blocks:
                        flush_line()
                        lines.append(text)
                        lines.append('')
                    else:
                        # Only add space if nodes aren't directly adjacent
                        if current_line and not current_line[-1].endswith(' '):
                            if node.prev and node.prev.text_content:
                                if node.parent != node.prev.parent or node.prev.next != node:
                                    current_line.append(' ')
                        current_line.append(text)
        
        flush_line()
        
        text = '\n'.join(lines)
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        return text.translate(str.maketrans({
            '\xa0': ' ', '\u2003': ' ',
            '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"'
        }))

    def contains_string(self, pattern):
        """Works for select files"""
        if self.extension in ['.htm', '.html', '.txt','.xml']:
            return bool(re.search(pattern, self.content))
        return False

    # Note: this method will be heavily modified in the future
    def parse(self):
        # check if we have already parsed the content
        if self.data:
            return self.data
        mapping_dict = None

        if self.extension == '.xml':
            if self.type in ['3', '4', '5', '3/A', '4/A', '5/A']:
                mapping_dict = dict_345

            self.data = xml2dict(content=self.content, mapping_dict=mapping_dict)

        # will deprecate this when we add html2dict
        elif self.extension in ['.htm', '.html','.txt']:

            if self.type == '10-K':
                mapping_dict = dict_10k
            elif self.type == '10-Q':
                mapping_dict = dict_10q
            elif self.type == '8-K':
                mapping_dict = dict_8k
            elif self.type == 'SC 13D':
                mapping_dict = dict_13d
            elif self.type == 'SC 13G':
                mapping_dict = dict_13g
            
            self.data = {}
            self.data['document'] = dict2dict(txt2dict(content=self.content, mapping_dict=mapping_dict))
        return self.data
    
    def write_json(self, output_filename=None):
        if not self.data:
            self.parse()
            
        with open(output_filename, 'w',encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)

    def to_tabular(self, accession_number=None):
        """
        Convert the document to a tabular format suitable for CSV output.
        
        Args:
            accession_number: Optional accession number to include in the output
            
        Returns:
            list: List of dictionaries, each representing a row in the tabular output
        """
        self.parse()
        
        # Common function to normalize and process dictionaries
        def process_records(records, mapping_dict, is_derivative=None):
            """
            Process records into a standardized tabular format
            
            Args:
                records: List or single dictionary of records to process
                mapping_dict: Dictionary mapping source keys to target keys
                is_derivative: Boolean flag for derivative securities (or None if not applicable)
                
            Returns:
                list: Processed records in tabular format
            """
            # Convert single dict to list for uniform processing
            if isinstance(records, dict):
                records = [records]
                
            # Flatten nested dictionaries
            flattened = self._flatten_dict(records)
            
            # Process each record
            result = []
            for item in flattened:
                # Normalize whitespace in all string values
                for key in item:
                    if isinstance(item[key], str):
                        item[key] = re.sub(r'\s+', ' ', item[key])
                        
                # Map keys according to the mapping dictionary
                mapped_item = {}
                for old_key, value in item.items():
                    target_key = mapping_dict.get(old_key, old_key)
                    mapped_item[target_key] = value
                    
                # Set derivative flags if applicable
                if is_derivative is not None:
                    mapped_item["isDerivative"] = 1 if is_derivative else 0
                    mapped_item["isNonDerivative"] = 0 if is_derivative else 1
                    
                # Ensure all expected columns exist
                output_columns = list(dict.fromkeys(mapping_dict.values()))
                ordered_item = {column: mapped_item.get(column, None) for column in output_columns}
                
                # Add accession number if provided
                if accession_number is not None:
                    ordered_item['accession'] = accession_number
                    
                result.append(ordered_item)
                
            return result
        
        # Handle different document types
        if self.type == "INFORMATION TABLE":
            # Information Table mapping dictionary
            info_table_mapping = {
                "nameOfIssuer": "nameOfIssuer", 
                "titleOfClass": "titleOfClass", 
                "cusip": "cusip", 
                "value": "value", 
                "shrsOrPrnAmt_sshPrnamt": "sshPrnamt", 
                "shrsOrPrnAmt_sshPrnamtType": "sshPrnamtType", 
                "investmentDiscretion": "investmentDiscretion", 
                "votingAuthority_Sole": "votingAuthoritySole", 
                "votingAuthority_Shared": "votingAuthorityShared", 
                "votingAuthority_None": "votingAuthorityNone", 
                "reportingOwnerCIK": "reportingOwnerCIK", 
                "putCall": "putCall", 
                "otherManager": "otherManager", 
                "figi": "figi"
            }
            
            # Process the information table
            info_table = self.data['informationTable']['infoTable']
            return process_records(info_table, info_table_mapping)
            
        elif self.type == "PROXY VOTING RECORD":
            # Proxy voting record mapping dictionary
            proxy_mapping = {
                'meetingDate': 'meetingDate',
                'isin': 'isin',  
                'cusip': 'cusip',
                'issuerName': 'issuerName',
                'voteDescription': 'voteDescription',
                'sharesOnLoan': 'sharesOnLoan',
                'vote_voteRecord_sharesVoted': 'sharesVoted',
                'voteCategories_voteCategory_categoryType': 'voteCategory', 
                'vote_voteRecord': 'voteRecord',
                'sharesVoted': 'sharesVoted', 
                'voteSource': 'voteSource', 
                'vote_voteRecord_howVoted': 'howVoted',
                'figi': 'figi', 
                'vote_voteRecord_managementRecommendation': 'managementRecommendation'
            }
            
            # Process proxy voting records if they exist
            all_results = []
            if 'proxyVoteTable' in self.data and 'proxyTable' in self.data['proxyVoteTable'] and self.data['proxyVoteTable']['proxyTable'] is not None:
                proxy_records = self.data['proxyVoteTable']['proxyTable']
                proxy_results = process_records(proxy_records, proxy_mapping)
                all_results.extend(proxy_results)
                
            return all_results
        
        elif self.type == "NPORT-P":
            # Proxy voting record mapping dictionary
            mapping = {
                'meetingDate': 'meetingDate',
                'isin': 'isin',  
                'cusip': 'cusip',
                'issuerName': 'issuerName',
                'voteDescription': 'voteDescription',
                'sharesOnLoan': 'sharesOnLoan',
                'vote_voteRecord_sharesVoted': 'sharesVoted',
                'voteCategories_voteCategory_categoryType': 'voteCategory', 
                'vote_voteRecord': 'voteRecord',
                'sharesVoted': 'sharesVoted', 
                'voteSource': 'voteSource', 
                'vote_voteRecord_howVoted': 'howVoted',
                'figi': 'figi', 
                'vote_voteRecord_managementRecommendation': 'managementRecommendation'
            }
            
            all_results = []
            data = (self.data.get('edgarSubmission', {}).get('formData', {}).get('invstOrSecs', {}).get('invstOrSec'))
            if data is not None:
                results = process_records(data, mapping)
                all_results.extend(results)
                
            return all_results
            
        elif self.type in ["3", "4", "5", "3/A", "4/A", "5/A"]:
            # Forms 3, 4, 5 mapping dictionary
            form_345_mapping = {
                # Flag fields (will be set programmatically)
                "isDerivative": "isDerivative",
                "isNonDerivative": "isNonDerivative",
                
                # Common fields across all types
                "securityTitle_value": "securityTitle",
                "transactionDate_value": "transactionDate",
                "documentType": "documentType",
                "transactionCoding_transactionFormType": "documentType",
                "transactionCoding_transactionCode": "transactionCode",
                "transactionAmounts_transactionAcquiredDisposedCode_value": "transactionCode",
                "transactionCoding_equitySwapInvolved": "equitySwapInvolved",
                "transactionTimeliness_value": "transactionTimeliness",
                "transactionAmounts_transactionShares_value": "transactionShares",
                "transactionAmounts_transactionPricePerShare_value": "transactionPricePerShare",
                "postTransactionAmounts_sharesOwnedFollowingTransaction_value": "sharesOwnedFollowingTransaction",
                "heldFollowingReport": "sharesOwnedFollowingTransaction",  # Form 3
                "ownershipNature_directOrIndirectOwnership_value": "ownershipType",
                "ownershipNature_natureOfOwnership_value": "ownershipType",
                "deemedExecutionDate": "deemedExecutionDate",
                "deemedExecutionDate_value": "deemedExecutionDate",
                
                # Derivative-specific fields
                "conversionOrExercisePrice_value": "conversionOrExercisePrice",
                "exerciseDate_value": "exerciseDate",
                "expirationDate_value": "expirationDate",
                "underlyingSecurity_underlyingSecurityTitle_value": "underlyingSecurityTitle",
                "underlyingSecurity_underlyingSecurityShares_value": "underlyingSecurityShares",
                "underlyingSecurity_underlyingSecurityValue_value": "underlyingSecurityValue",
                
                # Footnote fields
                "transactionPricePerShareFootnote": "transactionPricePerShareFootnote",
                "transactionAmounts_transactionPricePerShare_footnote": "transactionPricePerShareFootnote",
                "transactionCodeFootnote": "transactionCodeFootnote",
                "transactionAmounts_transactionAcquiredDisposedCode_footnote": "transactionCodeFootnote",
                "transactionCoding_footnote": "transactionCodeFootnote",
                "natureOfOwnershipFootnote": "natureOfOwnershipFootnote",
                "ownershipNature_natureOfOwnership_footnote": "natureOfOwnershipFootnote",
                "sharesOwnedFollowingTransactionFootnote": "sharesOwnedFollowingTransactionFootnote",
                "postTransactionAmounts_sharesOwnedFollowingTransaction_footnote": "sharesOwnedFollowingTransactionFootnote",
                "ownershipTypeFootnote": "ownershipTypeFootnote",
                "ownershipNature_directOrIndirectOwnership_footnote": "ownershipTypeFootnote",
                "securityTitleFootnote": "securityTitleFootnote",
                "securityTitle_footnote": "securityTitleFootnote",
                "transactionSharesFootnote": "transactionSharesFootnote",
                "transactionAmounts_transactionShares_footnote": "transactionSharesFootnote",
                "transactionDateFootnote": "transactionDateFootnote",
                "transactionDate_footnote": "transactionDateFootnote",
                "conversionOrExercisePriceFootnote": "conversionOrExercisePriceFootnote",
                "conversionOrExercisePrice_footnote": "conversionOrExercisePriceFootnote",
                "exerciseDateFootnote": "exerciseDateFootnote",
                "exerciseDate_footnote": "exerciseDateFootnote",
                "expirationDateFootnote": "expirationDateFootnote",
                "expirationDate_footnote": "expirationDateFootnote",
                "underlyingSecurityTitleFootnote": "underlyingSecurityTitleFootnote",
                "underlyingSecurity_underlyingSecurityTitle_footnote": "underlyingSecurityTitleFootnote",
                "underlyingSecuritySharesFootnote": "underlyingSecuritySharesFootnote",
                "underlyingSecurity_underlyingSecurityShares_footnote": "underlyingSecuritySharesFootnote",
                "underlyingSecurityValueFootnote": "underlyingSecurityValueFootnote",
                "underlyingSecurity_underlyingSecurityValue_footnote": "underlyingSecurityValueFootnote"
            }
            
            # Results container
            all_results = []
            
            # Process non-derivative transactions if they exist
            if 'nonDerivativeTable' in self.data['ownershipDocument'] and self.data['ownershipDocument']['nonDerivativeTable'] is not None:
                if 'nonDerivativeTransaction' in self.data['ownershipDocument']['nonDerivativeTable']:
                    non_deriv_trans = self.data['ownershipDocument']['nonDerivativeTable']['nonDerivativeTransaction']
                    non_deriv_results = process_records(non_deriv_trans, form_345_mapping, is_derivative=False)
                    all_results.extend(non_deriv_results)
                
                # Process non-derivative holdings (for Form 3)
                if 'nonDerivativeHolding' in self.data['ownershipDocument']['nonDerivativeTable']:
                    non_deriv_hold = self.data['ownershipDocument']['nonDerivativeTable']['nonDerivativeHolding']
                    non_deriv_hold_results = process_records(non_deriv_hold, form_345_mapping, is_derivative=False)
                    all_results.extend(non_deriv_hold_results)
            
            # Process derivative transactions if they exist
            if 'derivativeTable' in self.data['ownershipDocument'] and self.data['ownershipDocument']['derivativeTable'] is not None:
                if 'derivativeTransaction' in self.data['ownershipDocument']['derivativeTable']:
                    deriv_trans = self.data['ownershipDocument']['derivativeTable']['derivativeTransaction']
                    deriv_results = process_records(deriv_trans, form_345_mapping, is_derivative=True)
                    all_results.extend(deriv_results)
                
                # Process derivative holdings (for Form 3)
                if 'derivativeHolding' in self.data['ownershipDocument']['derivativeTable']:
                    deriv_hold = self.data['ownershipDocument']['derivativeTable']['derivativeHolding']
                    deriv_hold_results = process_records(deriv_hold, form_345_mapping, is_derivative=True)
                    all_results.extend(deriv_hold_results)
            
            return all_results
        
        else:
            raise ValueError(f"Document type '{self.type}' is not supported for tabular conversion")
    
    def write_csv(self, output_filename, accession_number=None):
            
        data = self.to_tabular(accession_number)

        if not data:

            return
        
        fieldnames = data[0].keys()
        
        with open(output_filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(data)

        
    def _document_to_section_text(self, document_data, parent_key=''):
        items = []
        
        if isinstance(document_data, dict):
            for key, value in document_data.items():
                # Build the section name
                section = f"{parent_key}_{key}" if parent_key else key
                
                # If the value is a dict, recurse
                if isinstance(value, dict):
                    items.extend(self._document_to_section_text(value, section))
                # If it's a list, handle each item
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            items.extend(self._document_to_section_text(item, f"{section}_{i+1}"))
                        else:
                            items.append({
                                'section': f"{section}_{i+1}",
                                'text': str(item)
                            })
                # Base case - add the item
                else:
                    items.append({
                        'section': section,
                        'text': str(value)
                    })
        
        return items

    # we'll modify this for every dict
    def _flatten_dict(self, d, parent_key=''):
        items = {}

        if isinstance(d, list):
            return [self._flatten_dict(item) for item in d]
                
        for k, v in d.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.update(self._flatten_dict(v, new_key))
            else:
                items[new_key] = str(v)
                    
        return items
   
   # this will all have to be changed. default will be to flatten everything
    def __iter__(self):
        self.parse()

        # Let's remove XML iterable for now

        # Handle text-based documents
        if self.extension in ['.txt', '.htm', '.html']:
            document_data = self.data
            if not document_data:
                return iter([])
                
            # Find highest hierarchy level from mapping dict
            highest_hierarchy = float('inf')
            section_type = None
            
            if self.type in ['10-K', '10-Q']:
                mapping_dict = dict_10k if self.type == '10-K' else dict_10q
            elif self.type == '8-K':
                mapping_dict = dict_8k
            elif self.type == 'SC 13D':
                mapping_dict = dict_13d
            elif self.type == 'SC 13G':
                mapping_dict = dict_13g
            else:
                return iter([])
                
            # Find section type with highest hierarchy number
            highest_hierarchy = -1  # Start at -1 to find highest
            for mapping in mapping_dict['rules']['mappings']:
                if mapping.get('hierarchy') is not None:
                    if mapping['hierarchy'] > highest_hierarchy:
                        highest_hierarchy = mapping['hierarchy']
                        section_type = mapping['name']
                        
            if not section_type:
                return iter([])
                
            # Extract sections of the identified type
            def find_sections(data, target_type):
                sections = []
                if isinstance(data, dict):
                    if data.get('type') == target_type:
                        sections.append({
                            'item': data.get('text', ''),
                            'text': flatten_hierarchy(data.get('content', []))
                        })
                    for value in data.values():
                        if isinstance(value, (dict, list)):
                            sections.extend(find_sections(value, target_type))
                elif isinstance(data, list):
                    for item in data:
                        sections.extend(find_sections(item, target_type))
                return sections
                
            return iter(find_sections(document_data, section_type))
            
        return iter([])
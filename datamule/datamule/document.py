import json
import csv
import re
from doc2dict import xml2dict, txt2dict, dict2dict
from doc2dict.mapping import flatten_hierarchy
from .mapping_dicts.txt_mapping_dicts import dict_10k, dict_10q, dict_8k, dict_13d, dict_13g
from .mapping_dicts.xml_mapping_dicts import dict_345
from selectolax.parser import HTMLParser

class Document:
    def __init__(self, type, content, extension):
        
        self.type = type
        extension = extension.lower()
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
            if self.type in ['3', '4', '5']:
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
        self.parse()

        if self.type == "INFORMATION TABLE":
            info_table = self.data['informationTable']['infoTable']
            if isinstance(info_table, dict):
                info_table = [info_table]

            flattened = self._flatten_dict(info_table)

            # Original field names
            original_columns = [
                "nameOfIssuer", "titleOfClass", "cusip", "value", 
                "shrsOrPrnAmt_sshPrnamt", "shrsOrPrnAmt_sshPrnamtType", 
                "investmentDiscretion", "votingAuthority_Sole", 
                "votingAuthority_Shared", "votingAuthority_None", 
                "reportingOwnerCIK", "putCall", "otherManager", 'figi'
            ]
                
            # Define mapping from original to camelCase field names
            field_mapping = {
                "shrsOrPrnAmt_sshPrnamt": "sshPrnamt",
                "shrsOrPrnAmt_sshPrnamtType": "sshPrnamtType",
                "votingAuthority_Sole": "votingAuthoritySole",
                "votingAuthority_Shared": "votingAuthorityShared",
                "votingAuthority_None": "votingAuthorityNone"
            }
                
            # Create the new expected columns list with mapped field names
            expected_columns = []
            for column in original_columns:
                if column in field_mapping:
                    expected_columns.append(field_mapping[column])
                else:
                    expected_columns.append(column)
                
            # Process each item in the flattened data
            for item in flattened:
                # Remove newlines from items
                for key in item:
                    if isinstance(item[key], str):
                        item[key] = re.sub(r'\s+', ' ', item[key])
                    
                new_item = {}
                for key, value in item.items():
                    # Apply the mapping if the key is in our mapping dictionary
                    if key in field_mapping:
                        new_item[field_mapping[key]] = value
                    else:
                        new_item[key] = value
                    
                # Update the original item with the new keys
                item.clear()
                item.update(new_item)
                    
                # Ensure all expected columns exist
                for column in expected_columns:
                    if column not in item:
                        item[column] = None

                item['accession'] = accession_number
            
            # Add this block to reorder the items to match the expected order
            ordered_columns = ["nameOfIssuer", "titleOfClass", "cusip", "value", "sshPrnamt", "sshPrnamtType",
                            "investmentDiscretion", "votingAuthoritySole", "votingAuthorityShared", "votingAuthorityNone",
                            "reportingOwnerCIK", "putCall", "otherManager", "figi"]
            if accession_number is not None:
                ordered_columns.append("accession")
                
            ordered_data = []
            for item in flattened:
                ordered_item = {column: item.get(column, None) for column in ordered_columns}
                ordered_data.append(ordered_item)
                
            return ordered_data
        
        elif self.type in ["3", "4", "5"]:
            # Master mapping dictionary - includes all possible fields
            # The order of this dictionary will determine the output column order
            master_mapping_dict = {
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
            
            # Get the unique target column names in order from the mapping dictionary
            output_columns = []
            for _, target_key in master_mapping_dict.items():
                if target_key not in output_columns:
                    output_columns.append(target_key)
            
            # Process function that handles any table type
            def process_table(table_data, is_derivative):
                if isinstance(table_data, dict):
                    table_data = [table_data]
                
                flattened = self._flatten_dict(table_data)
                
                # Apply mapping to the flattened data and ensure all expected columns are present
                mapped_data = []
                for item in flattened:
                    mapped_item = {}
                    # First, apply the mapping
                    for old_key, value in item.items():
                        target_key = master_mapping_dict.get(old_key, old_key)
                        mapped_item[target_key] = value
                    
                    # Set the derivative/non-derivative flags
                    mapped_item["isDerivative"] = 1 if is_derivative else 0
                    mapped_item["isNonDerivative"] = 0 if is_derivative else 1
                    
                    # Create a new ordered dictionary with all columns
                    ordered_item = {}
                    for column in output_columns:
                        ordered_item[column] = mapped_item.get(column, None)
                    
                    # Add accession_number if available
                    if accession_number is not None:
                        ordered_item['accession_number'] = accession_number
                    
                    mapped_data.append(ordered_item)
                
                return mapped_data
            
            # Results container
            all_results = []
            
            # Process non-derivative transactions if they exist
            if 'nonDerivativeTable' in self.data['ownershipDocument'] and self.data['ownershipDocument']['nonDerivativeTable'] is not None:
                if 'nonDerivativeTransaction' in self.data['ownershipDocument']['nonDerivativeTable']:
                    non_deriv_trans = self.data['ownershipDocument']['nonDerivativeTable']['nonDerivativeTransaction']
                    non_deriv_results = process_table(non_deriv_trans, is_derivative=False)
                    all_results.extend(non_deriv_results)
                
                # Process non-derivative holdings (for Form 3)
                if 'nonDerivativeHolding' in self.data['ownershipDocument']['nonDerivativeTable']:
                    non_deriv_hold = self.data['ownershipDocument']['nonDerivativeTable']['nonDerivativeHolding']
                    non_deriv_hold_results = process_table(non_deriv_hold, is_derivative=False)
                    all_results.extend(non_deriv_hold_results)
            
            # Process derivative transactions if they exist
            if 'derivativeTable' in self.data['ownershipDocument'] and self.data['ownershipDocument']['derivativeTable'] is not None:
                if 'derivativeTransaction' in self.data['ownershipDocument']['derivativeTable']:
                    deriv_trans = self.data['ownershipDocument']['derivativeTable']['derivativeTransaction']
                    deriv_results = process_table(deriv_trans, is_derivative=True)
                    all_results.extend(deriv_results)
                
                # Process derivative holdings (for Form 3)
                if 'derivativeHolding' in self.data['ownershipDocument']['derivativeTable']:
                    deriv_hold = self.data['ownershipDocument']['derivativeTable']['derivativeHolding']
                    deriv_hold_results = process_table(deriv_hold, is_derivative=True)
                    all_results.extend(deriv_hold_results)

            # check if any rows not in the mapping dict, raise error if so
            for item in all_results:
                for key in item.keys():
                    if key not in master_mapping_dict.values() and key != 'accession_number':
                        raise ValueError(f"Key '{key}' not found in mapping dictionary")

            
            return all_results
        else:
            raise ValueError("sorry, rejigging conversion to tabular format")
        
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
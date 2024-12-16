import json
import csv
from .parser.document_parsing.sec_parser import Parser
from .helper import convert_to_dashed_accession

# we need to modify parse filing to take option in memory

parser = Parser()

class Document:
    def __init__(self, type, filename):
        self.type = type
        self.filename = filename

        self.data = None

    def parse(self):
        self.data = parser.parse_filing(self.filename, self.type)
        return self.data
    
    def write_json(self, output_filename=None):
        if not self.data:
            raise ValueError("No data to write. Parse filing first.")
            
        if output_filename is None:
            output_filename = f"{self.filename.rsplit('.', 1)[0]}.json"
            
        with open(output_filename, 'w') as f:
            json.dump(self.data, f, indent=2)

    def write_csv(self, output_filename=None, accession_number=None):
        if self.data is None:
            raise ValueError("No data available. Please call parse_filing() first.")

        if output_filename is None:
            output_filename = f"{self.filename.rsplit('.', 1)[0]}.csv"

        with open(output_filename, 'w', newline='') as csvfile:
            if not self.data:
                return output_filename

            has_document = any('document' in item for item in self.data)
            
            if has_document and 'document' in self.data:
                writer = csv.DictWriter(csvfile, ['section', 'text'], quoting=csv.QUOTE_ALL)
                writer.writeheader()
                flattened = self._flatten_dict(self.data['document'])
                for section, text in flattened.items():
                    writer.writerow({'section': section, 'text': text})
            else:
                fieldnames = list(self.data[0].keys())
                if accession_number:
                    fieldnames.append('Accession Number')
                writer = csv.DictWriter(csvfile, fieldnames, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                for row in self.data:
                    if accession_number:
                        row['Accession Number'] = convert_to_dashed_accession(accession_number)
                    writer.writerow(row)

        return output_filename
    
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
   
    def __iter__(self):
        if not self.data:
            self.parse()

        if self.type == 'INFORMATION TABLE':
            return iter(self.data)
        elif self.type == '8-K':
            return iter(self._document_to_section_text(self.data['document']))
        elif self.type == '10-K':
            return iter(self._document_to_section_text(self.data['document']))
        elif self.type == '10-Q':
            return iter(self._document_to_section_text(self.data['document']))
        elif self.type in ['3', '4', '5']:
            return iter(self._flatten_dict(self.data['holdings']))
        elif self.type == 'D':
            return iter(self._flatten_dict(self.data['document']['relatedPersonsList']['relatedPersonInfo']))
        elif self.type == 'NPORT-P':
            return iter(self._flatten_dict(self.data['document']['formData']['invstOrSecs']['invstOrSec']))
        elif self.type == 'SC 13D':
            return iter(self._document_to_section_text(self.data['document']))
        elif self.type == 'SC 13G':
            return iter(self._document_to_section_text(self.data['document']))
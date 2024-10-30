import json
import csv
from .parser.sec_parser import Parser
from .helper import convert_to_dashed_accession

class Filing:
   def __init__(self, filename, filing_type):
       self.filename = filename
       self.parser = Parser()
       self.data = None
       self.filing_type = filing_type

   def parse_filing(self):
       self.data = self.parser.parse_filing(self.filename, self.filing_type)
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

   def _flatten_dict(self, d, parent_key=''):
       items = {}
       for k, v in d.items():
           new_key = f"{parent_key}_{k}" if parent_key else k
           if isinstance(v, dict):
               items.update(self._flatten_dict(v, new_key))
           else:
               items[new_key] = v
       return items
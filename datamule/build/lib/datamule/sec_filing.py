import csv

from .parser.sec_parser import Parser
from .helper import convert_to_dashed_accession

class Filing:
    def __init__(self, filename,filing_type):
        self.filename = filename
        self.parser = Parser()
        self.data = None
        self.filing_type = filing_type

    def parse_filing(self):
        self.data = self.parser.parse_filing(self.filename, self.filing_type)
        return self.data

    def write_csv(self, output_filename=None, accession_number=None):
        if self.data is None:
            raise ValueError("No data available. Please call parse_filing() first.")

        if not isinstance(self.data, list) or not all(isinstance(item, dict) for item in self.data):
            raise ValueError("Data is not in the expected format for CSV conversion.")

        if output_filename is None:
            output_filename = f"{self.filename.rsplit('.', 1)[0]}.csv"

        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            if not self.data:
                return output_filename

            fieldnames = list(self.data[0].keys())
            if accession_number is not None:
                fieldnames.append('Accession Number')

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

            writer.writeheader()
            for row in self.data:
                row_data = {k: self._csv_safe_value(v) for k, v in row.items()}
                if accession_number is not None:
                    row_data['Accession Number'] = convert_to_dashed_accession(accession_number)
                writer.writerow(row_data)

        return output_filename

    @staticmethod
    def _csv_safe_value(value):
        if value is None:
            return ''
        if isinstance(value, (int, float)):
            return value
        return str(value).replace('\n', ' ').replace('\r', '')

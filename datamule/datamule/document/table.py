from .mapping_dicts import *
# need to check if mappings correctly create new columns
class Table():
    def __init__(self, data, type,accession):
        if isinstance(data,dict):
            data = [data]
        self.type = type
        self.data = data
        self.accession = accession
        self.columns = self.determine_columns()

    def determine_columns(self):
        if len(self.data) == 0:
            return []
        return self.data[0].keys()

    def add_column(self,column_name,value):
        for row in self.data:
            row[column_name] = value

    def map_data(self):
        # Add the accession column to all rows first, ensuring it will be first
        self.add_column('accession', self.accession)
        
        # Define the mapping dictionary for each table type
        if self.type == 'non_derivative_holding_ownership':
            mapping_dict = non_derivative_holding_ownership_dict
        elif self.type == 'non_derivative_transaction_ownership':
            mapping_dict = non_derivative_transaction_ownership_dict
        elif self.type == 'derivative_transaction_ownership':
            mapping_dict = derivative_transaction_ownership_dict
        elif self.type == 'derivative_holding_ownership':
            mapping_dict = derivative_holding_ownership_dict
        else:
            mapping_dict = {}
        
        # Update mapping dictionary to include accession at the beginning
        # Create a new mapping with accession as the first key
        new_mapping = {'accession': 'accession'}
        # Add the rest of the mapping
        new_mapping.update(mapping_dict)
        mapping_dict = new_mapping

        # apply the mapping to the data
        for row in self.data:
            ordered_row = {}
            # First add all keys from the mapping dict in order
            for old_key, new_key in mapping_dict.items():
                if old_key in row:
                    ordered_row[new_key] = row.pop(old_key)
                else:
                    # if the old key is not present, set the new key to None
                    ordered_row[new_key] = None
            
            # Then add any remaining keys that weren't in the mapping
            for key, value in row.items():
                ordered_row[key] = value
            
            # Replace the original row with the ordered row
            row.clear()
            row.update(ordered_row)

        self.determine_columns()

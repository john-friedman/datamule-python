from .mapping_dicts import *
class Table():
    def __init__(self, data, type):
        if isinstance(data,dict):
            data = [data]
        self.type = type
        self.data = data
        self.map_data()
        self.columns = self.determine_columns()

    def determine_columns(self):
        if len(self.data) == 0:
            return []
        return self.data[0].keys()

    def add_column(self,column_name,value):
        for row in self.data:
            row[column_name] = value

    def map_data(self):
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

        # apply the mapping to the data
        for row in self.data:
            for old_key, new_key in mapping_dict.items():
                if old_key in row:
                    row[new_key] = row.pop(old_key)
                else:
                    # if the old key is not present, set the new key to None
                    row[new_key] = None


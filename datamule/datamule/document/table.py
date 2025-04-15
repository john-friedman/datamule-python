class Table():
    def __init__(self, data, type):
        self.data = data
        self.type = type

    def add_column(self,column_name,value):
        for row in self.data:
            row[column_name] = value

    def map_data(self,mapping_dict):
        pass
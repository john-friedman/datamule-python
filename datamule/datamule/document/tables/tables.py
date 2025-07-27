from .ownership_tables import ownership_tables_dict
from .utils import safe_get, flatten_dict
# will add filing date param later? or extension
all_tables_dict = {
    ('3','3') : ownership_tables_dict,
    ('3/A','3/A') : ownership_tables_dict,
    ('4','4') : ownership_tables_dict,
    ('4/A','4/A') : ownership_tables_dict,
    ('5','5') : ownership_tables_dict,
    ('5/A','5/A') : ownership_tables_dict,
}


def seperate_data(tables_dict, data):
    data_list = []
    
    for table_name, config in tables_dict.items():
        path = config['path']
        
        # Extract data at the specific path
        table_data = safe_get(data, path.split('.'))
        if not table_data:
            continue
            
        # Find sub-paths to exclude (only for paths that have sub-tables)
        sub_paths = [other_path for other_path in [c['path'] for c in tables_dict.values()] 
                    if other_path.startswith(path + '.')]
        
        # Only apply exclusions if this path has sub-paths AND the data is a dict
        if sub_paths and isinstance(table_data, dict):
            exclude_keys = {sp.split('.')[len(path.split('.'))] for sp in sub_paths}
            table_data = {k: v for k, v in table_data.items() if k not in exclude_keys}
        
        data_list.append((table_name, table_data))
    
    return data_list

def apply_mapping(flattened_data, mapping_dict, accession):
    """Apply mapping to flattened data and add accession"""
    # Create ordered row starting with accession
    ordered_row = {'accession': accession}
    
    # Apply mapping for all other keys
    for old_key, new_key in mapping_dict.items():
        if old_key in flattened_data:
            ordered_row[new_key] = flattened_data.pop(old_key)
    
    # Then add any remaining keys that weren't in the mapping
    for key, value in flattened_data.items():
        ordered_row[key] = value
    
    return ordered_row

# should have table type, accession, data
class Table:
    def __init__(self,data,name,accession):
        self.data = data
        self.name = name
        self.accession = accession


class Tables():
    def __init__(self, submission_type,document_type,accession,data):
        self.submission_type = submission_type
        self.document_type = document_type
        self.accession = accession
        self.data = data

        # to fill in
        self.tables = []

        self.parse_tables()

    def parse_tables(self):
        # first select dict

        try:
            tables_dict = all_tables_dict[(self.submission_type,self.document_type)]
        except:
            raise ValueError(f"Table not found: {self.submission_type,self.document_type}")
        
        # now get the dicts from the data
        data_dicts = seperate_data(tables_dict,self.data)
        
        # now flatten
        data_dicts = [(x,flatten_dict(y)) for x,y in data_dicts]
        
        for table_name, flattened_data in data_dicts:
            mapping_dict = tables_dict[table_name]['mapping']
            mapped_data = apply_mapping(flattened_data, mapping_dict, self.accession)
            self.tables.append(Table(mapped_data, table_name, self.accession))
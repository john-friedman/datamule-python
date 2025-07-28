from .tables_ownership import config_ownership
from .tables_13fhr import mapping_13fhr 
from .tables_informationtable import config_information_table
from .tables_25nse import config_25nse
from .tables_npx import config_npx
from .tables_sbsef import config_sbsef
from .tables_sdr import config_sdr
from .tables_proxyvotingrecord import config_proxyvotingrecord
 
from .utils import safe_get, flatten_dict
# will add filing date param later? or extension
all_tables_dict = {
    '3' : config_ownership,
    '3/A' : config_ownership,
    '4' : config_ownership,
    '4/A' : config_ownership,
    '5' : config_ownership,
    '5/A' : config_ownership,
    '13F-HR' : mapping_13fhr,
    '13F-HR/A' : mapping_13fhr,
    '13F-NT' : mapping_13fhr,
    '13F-NT/A' : mapping_13fhr,
    'INFORMATION TABLE' : config_information_table,
    '25-NSE' : config_25nse,
    '25-NSE/A' : config_25nse,
    'N-PX' : config_npx,
    'N-PX/A' : config_npx,
    'SBSEF' : config_sbsef,
    'SBSEF/A' : config_sbsef,
    'SBSEF-V' : config_sbsef,
    'SBSEF-W' : config_sbsef,
    'SDR' : config_sdr,
    'SDR/A' : config_sdr,
    'SDR-W' : config_sdr,
    'SDR-A' : config_sdr,
    'PROXY VOTING RECORD' : config_proxyvotingrecord,
}

# process_ex102_abs will need to be done later
# process d
# 144

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
    
    # Handle case where flattened_data is a list of dictionaries
    if isinstance(flattened_data, list):
        results = []
        for data_dict in flattened_data:
            results.append(apply_mapping(data_dict, mapping_dict, accession))
        return results
    
    # Original logic for single dictionary
    ordered_row = {'accession': accession}
    
    # Apply mapping for all other keys
    for old_key, new_key in mapping_dict.items():
        if old_key in flattened_data:
            ordered_row[new_key] = flattened_data.pop(old_key)
        else:
            ordered_row[new_key] = None
    
    # Add any remaining keys that weren't in the mapping
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
    def __init__(self,document_type,accession,data):
        self.document_type = document_type
        self.accession = accession
        self.data = data

        # to fill in
        self.tables = []

        self.parse_tables()

    def parse_tables(self):
        # first select dict

        try:
            tables_dict = all_tables_dict[self.document_type]
        except:
            raise ValueError(f"Table not found: {self.document_type}.")
        
        # now get the dicts from the data
        data_dicts = seperate_data(tables_dict,self.data)
        
        # now flatten
        data_dicts = [(x,flatten_dict(y)) for x,y in data_dicts]
        
        for table_name, flattened_data in data_dicts:
            mapping_dict = tables_dict[table_name]['mapping']
            mapped_data = apply_mapping(flattened_data, mapping_dict, self.accession)
            self.tables.append(Table(mapped_data, table_name, self.accession))
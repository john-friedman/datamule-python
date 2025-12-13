from .tables_ownership import config_ownership
from .tables_13fhr import config_13fhr
from .tables_informationtable import config_information_table
from .tables_25nse import config_25nse
from .tables_npx import config_npx
from .tables_sbsef import config_sbsef
from .tables_sdr import config_sdr
from .tables_proxyvotingrecord import config_proxyvotingrecord
from doc2dict.utils.format_dict import _format_table
 
from .utils import safe_get, flatten_dict
import re
# will add filing date param later? or extension
all_tables_dict = {
    '3' : config_ownership,
    '3/A' : config_ownership,
    '4' : config_ownership,
    '4/A' : config_ownership,
    '5' : config_ownership,
    '5/A' : config_ownership,
    '13F-HR' : config_13fhr,
    '13F-HR/A' : config_13fhr,
    '13F-NT' : config_13fhr,
    '13F-NT/A' : config_13fhr,
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

def apply_mapping(flattened_data, mapping_dict, accession, must_exist_in_mapping=False):
    """Apply mapping to flattened data and add accession"""
    
    # Handle case where flattened_data is a list of dictionaries
    if isinstance(flattened_data, list):
        results = []
        for data_dict in flattened_data:
            results.extend(apply_mapping(data_dict, mapping_dict, accession,must_exist_in_mapping))
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
    if not must_exist_in_mapping:
        for key, value in flattened_data.items():
            ordered_row[key] = value
    
    return [ordered_row]

# TODO, move from dict {} to [[]]
class Table:
    def __init__(self,data,name,accession,description = None):
        self.data = data
        if data != []:
            try:
                self.columns = data[0].keys() # handle xml tables
            except:
                self.columns = data[0] # handle html tables
        self.name = name
        self.accession = accession
        self.description = description

    # TODO MADE IN A HURRY #
    def __str__(self):
        formatted_table = _format_table(self.data)
        if isinstance(formatted_table, list):
            table_str = '\n'.join(formatted_table)
        else:
            table_str = str(formatted_table)
        return f"Table '{self.name}' ({self.accession}) - {len(self.data) if isinstance(self.data, list) else 'N/A'} rows\ndescription: {self.description if self.description else ''}\n{table_str}"


class Tables():
    def __init__(self,document_type,accession):
        self.document_type = document_type
        self.accession = accession
        self.tables = []

    def parse_tables(self,data,must_exist_in_mapping=True):
        self.data = data

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
            mapped_data = apply_mapping(flattened_data, mapping_dict, self.accession,must_exist_in_mapping)
            self.tables.append(Table(mapped_data, table_name, self.accession))
        
    def add_table(self,data,name,description=None):
        self.tables.append(Table(data=data,name=name,accession=self.accession,description=description))

    def get_tables(self, description_regex=None, name=None, contains_regex=None):
        matching_tables = []
        
        for table in self.tables:
            # Check name match (exact match)
            if name is not None:
                if table.name == name:
                    matching_tables.append(table)
                    continue
            
            # Check description regex match
            if description_regex is not None and table.description is not None:
                if re.search(description_regex, table.description):
                    # If contains_regex is also specified, need to check that too
                    if contains_regex is not None:
                        if self._check_contains_regex(table, contains_regex):
                            matching_tables.append(table)
                    else:
                        matching_tables.append(table)
                    continue
            
            # Check contains_regex match (only if description_regex didn't already handle it)
            if contains_regex is not None and description_regex is None and name is None:
                if self._check_contains_regex(table, contains_regex):
                    matching_tables.append(table)
        
        return matching_tables

    def _check_contains_regex(self, table, contains_regex):
        # Convert all patterns to compiled regex objects
        compiled_patterns = [re.compile(pattern) for pattern in contains_regex]
        
        # Track which patterns have been matched
        patterns_matched = [False] * len(compiled_patterns)
        
        # Iterate through all cells in table.data
        for row in table.data:
            for cell in row:
                # Convert cell to string for regex matching
                cell_str = str(cell)
                
                # Check each pattern that hasn't been matched yet
                for i, pattern in enumerate(compiled_patterns):
                    if not patterns_matched[i]:
                        if pattern.search(cell_str):
                            patterns_matched[i] = True
                
                # Early exit if all patterns have been matched
                if all(patterns_matched):
                    return True
        
        # Return True only if all patterns were matched
        return all(patterns_matched)
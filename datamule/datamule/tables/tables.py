from doc2dict.utils.format_dict import _format_table
 
from .utils import safe_get, flatten_dict
from .tableparser import parser
import re

# may need to move to doc2dict
def extract_text(dict_list):
    if isinstance(dict_list, dict):
        dict_list = [dict_list]
    return '\n'.join(filter(None, [d.get('text') or d.get('textsmall') for d in dict_list]))

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


class Table:
    def __init__(self, data_raw, name, accession, description=None, preamble=None, footnotes=None, postamble=None):
        self.data_raw = data_raw
        
        # Clean the data - strip dict wrappers and keep just table content
        if data_raw != []:
            try:
                # Handle xml tables - already list of dicts
                self.columns = data_raw[0].keys()
                self.data = [{**row, '_table': name} for row in data_raw]
            except:
                # Handle html tables - already list of lists
                self.columns = data_raw[0]
                self.data = data_raw
        else:
            self.columns = []
            self.data = []
                
        self.name = name
        self.accession = accession
        self.description = description
        
        # Store raw versions
        self.preamble_raw = preamble
        self.footnotes_raw = footnotes if footnotes is not None else []
        self.postamble_raw = postamble
        
        # Process into clean versions
        self.preamble = extract_text(preamble) if preamble is not None else None
        self.postamble = extract_text(postamble) if postamble is not None else None
        
        # Process footnotes into list of (id, text) tuples
        self.footnotes = []
        if footnotes is not None:
            for footnote in footnotes:
                footnote_id = footnote.get('footnote_id', '')
                footnote_text = extract_text(footnote)
                self.footnotes.append((footnote_id, footnote_text))

    def __str__(self):
        parts = []
        
        # Header with name and accession
        parts.append(f"Table '{self.name}' ({self.accession}) - {len(self.data) if isinstance(self.data, list) else 'N/A'} rows")
        
        # Description
        if self.description:
            parts.append(f"Description: {self.description}")
        
        # Preamble
        if self.preamble:
            parts.append(f"\nPreamble: {self.preamble}")
        
        # The actual table
        if self.data and isinstance(self.data[0], dict):
            headers = list(self.columns)
            table_as_lists = [headers] + [[str(row.get(h, '')) for h in headers] for row in self.data]
            formatted_table = _format_table(table_as_lists)
        else:
            formatted_table = _format_table(self.data)
        
        if isinstance(formatted_table, list):
            table_str = '\n'.join(formatted_table)
        else:
            table_str = str(formatted_table)
        parts.append(f"\n{table_str}")
        
        # Footnotes
        if self.footnotes:
            parts.append(f"\nFootnotes:")
            for footnote_id, footnote_text in self.footnotes:
                parts.append(f"{footnote_id}: {footnote_text}")
        
        # Postamble
        if self.postamble:
            parts.append(f"\nPostamble: {self.postamble}")
        
        return '\n'.join(parts)
    
    def __iter__(self):
        yield from self.data


class Tables():
    def __init__(self, document_type, accession):
        self.document_type = document_type
        self.accession = accession
        self.tables = []

    def __iter__(self):
        for table in self.tables:
            yield from table.data

    def __len__(self):
        return sum(len(t.data) for t in self.tables)

    def __bool__(self):
        return any(t.data for t in self.tables)

    def __getitem__(self, idx):
        # flatten lazily to a list for indexing
        flat = [row for t in self.tables for row in t.data]
        return flat[idx]

    def parse_xml_bytes(self, content, mapping_dict):
        
        rows = parser(content, mapping_dict)
        tables = [(t, [{k: v for k, v in r.items()} for r in rows if r['_table'] == t]) for t in {r['_table'] for r in rows}]
        for table in tables:
            self.tables.append(Table(table[1], table[0], self.accession))
        
    def add_table(self, data, name, description=None, preamble=None, footnotes=None, postamble=None):
        """Add a table with optional metadata components"""
        self.tables.append(Table(
            data_raw=data,
            name=name,
            accession=self.accession,
            description=description,
            preamble=preamble,
            footnotes=footnotes,
            postamble=postamble
        ))

    def get_tables(self, description_regex=None, description_fields=['preamble', 'postamble', 'footnotes'], name=None, contains_regex=None, title_regex=None):
        matching_tables = []
        
        for table in self.tables:
            # Check name match (exact match)
            if name is not None:
                if table.name == name:
                    matching_tables.append(table)
                    continue
            

            if title_regex is not None:
                if table.name and re.search(title_regex, table.name):
                    matching_tables.append(table)
                    continue
            
            # Check description regex match
            if description_regex is not None:
                description_matched = False
                
                # Search in specified fields
                for field in description_fields:
                    field_value = getattr(table, field, None)
                    if field_value is not None:
                        # Handle both string and list formats
                        if isinstance(field_value, str):
                            if re.search(description_regex, field_value):
                                description_matched = True
                                break
                        elif isinstance(field_value, list):
                            # For footnotes, it's now a list of tuples (id, text)
                            # Join the text parts and search
                            combined_text = ' '.join(text for _, text in field_value)
                            if re.search(description_regex, combined_text):
                                description_matched = True
                                break
                
                if description_matched:
                    # If contains_regex is also specified, need to check that too
                    if contains_regex is not None:
                        if self._check_contains_regex(table, contains_regex):
                            matching_tables.append(table)
                    else:
                        matching_tables.append(table)
                    continue
            
            # Check contains_regex match (only if description_regex didn't already handle it)
            if contains_regex is not None and description_regex is None and name is None and title_regex is None:
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
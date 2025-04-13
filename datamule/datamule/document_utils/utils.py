class Table():
    def __init__(self, data, type):
        self.data = data
        self.type = type

def _flatten_dict(d, parent_key=''):
    items = {}

    if isinstance(d, list):
        return [_flatten_dict(item) for item in d]
            
    for k, v in d.items():
        new_key = f"{parent_key}_{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.update(_flatten_dict(v, new_key))
        else:
            items[new_key] = str(v)
                
    return items

# coerce date!
def coerce_date(date_str):
    pass

def to_tabular(data, mapping_dict):
    # Flatten the input data
    flattened_data = _flatten_dict(data)
    
    # Create a new dictionary with mapped keys
    mapped_data = {}
    
    # Track unmapped keys
    unmapped_keys = []
    
    # Map the keys and collect unmapped keys
    for key, value in flattened_data.items():
        if key in mapping_dict:
            mapped_key = mapping_dict[key]
            mapped_data[mapped_key] = value
        else:
            unmapped_keys.append(key)
    
    # Print warnings for unmapped keys
    if unmapped_keys:
        print(f"Warning: {len(unmapped_keys)} keys found in data but not in mapping dictionary:")
        for key in unmapped_keys:
            print(f"  - {key}")
    
    return mapped_data

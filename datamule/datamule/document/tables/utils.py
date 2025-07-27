def safe_get(d, keys, default=None):
    """Safely access nested dictionary keys"""
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

# may modify this in the future to better account for lsits
def flatten_dict(d, parent_key=''):
    items = {}

    if isinstance(d, list):
        return [flatten_dict(item) for item in d]
            
    for k, v in d.items():
        new_key = f"{parent_key}_{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key))
        else:
            items[new_key] = str(v)
                
    return items
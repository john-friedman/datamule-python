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


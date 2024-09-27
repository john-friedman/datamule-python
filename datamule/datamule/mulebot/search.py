import difflib
from typing import Dict, List, Any

def search_filing(query: str, nested_dict: Dict[str, Any], max_matches: int = 20, score_cutoff: float = 0.6) -> List[Dict[str, Any]]:
    max_matches = min(max_matches, 20)
    query = query.lower()  # Convert query to lowercase
    
    def flatten_dict(d: Dict[str, Any], parent_path: List[str] = None) -> List[Dict[str, Any]]:
        parent_path = parent_path or []
        items = []
        
        if isinstance(d, dict):
            for k, v in d.items():
                new_path = parent_path + [k]
                if k == 'title' and isinstance(v, str):
                    items.append({'path': new_path, 'title': v, 'title_lower': v.lower()})
                items.extend(flatten_dict(v, new_path))
        elif isinstance(d, list):
            for i, item in enumerate(d):
                new_path = parent_path + [str(i)]
                items.extend(flatten_dict(item, new_path))
        
        return items

    flat_list = flatten_dict(nested_dict)
    all_titles_lower = [item['title_lower'] for item in flat_list]
    
    matches = difflib.get_close_matches(query, all_titles_lower, n=max_matches, cutoff=score_cutoff)
    
    results = []
    for match in matches:
        similarity = difflib.SequenceMatcher(None, query, match).ratio()
        for item in flat_list:
            if item['title_lower'] == match:
                # Navigate to the correct nested dictionary
                d = nested_dict
                for key in item['path'][:-1]:  # Exclude the last 'title' key
                    if key.isdigit():
                        d = d[int(key)]
                    else:
                        d = d[key]
                results.append({
                    'path': '.'.join(item['path'][:-1]),  # Exclude the last 'title' key
                    'content': d,
                    'similarity': similarity
                })
                break
    
    results.sort(key=lambda x: x['similarity'], reverse=True)


    return [item['content'] for item in results[:max_matches]]
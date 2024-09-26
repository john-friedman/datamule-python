import difflib

# we will need to write better search algorithms

def fuzzy_search(query, labels, max_matches=20, score_cutoff=0.6):
    # Ensure max_matches is no more than 20
    max_matches = min(max_matches, 20)
    
    
    # Use difflib to get close matches
    matches = difflib.get_close_matches(query, labels, n=max_matches, cutoff=score_cutoff)
    
    # Calculate similarity scores
    results = []
    for match in matches:
        results.append(match)
    
    # Sort results by similarity score in descending order
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Return at most max_matches results
    return results[:max_matches]
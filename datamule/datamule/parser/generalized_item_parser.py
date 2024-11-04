# Parses e.g. 10-K, 10-Q,..... any form with items and/or parts
from .helper import load_file_content, clean_title
from pathlib import Path
import re

# example
mapping_dict_10k = {
   'part1': {'item1', 'item1a', 'item1b', 'item1c', 'item2', 'item3', 'item4'},
   'part2': {'item5', 'item6', 'item7', 'item7a', 'item8', 'item9', 'item9a', 'item9b', 'item9c'},
   'part3': {'item10', 'item11', 'item12', 'item13', 'item14'},
   'part4': {'item15', 'item16'}
}

pattern = re.compile(r'^\s*(item|signature(?:\.?s)?)\s+\d+', re.I | re.M)

def find_anchors(content):
   anchors = []
   prev_title = None
   
   for part_match in pattern.finditer(content):
       title = clean_title(part_match.group())
       # Skip duplicates, e.g. "item 1" and "item1 continued"
       if prev_title == title:
           continue
       prev_title = title
       anchors.append((title, part_match.start()))
   
   return anchors

# I think this works, but I haven't tested it yet. Test with 10k and 10ksb
def map_sections(content, anchors, mapping_dict):
    result = {}
    positions = anchors + [('end', len(content))]
    
    for i, (title, start) in enumerate(positions[:-1]):
        _, next_start = positions[i + 1]
        section_text = content[start:next_start].strip()
        
        # Find which part contains this item
        for part, items in mapping_dict.items():
            if title.lower() in items:
                if part not in result:
                    result[part] = {}
                result[part][title] = section_text
                break

    return result

# TODO, I think we can start where a mostly complete sequence starts.
# I would like to generalize for 8-K structure as well...
def find_content_start(content):
    pass

def generalized_parser(filename,mapping_dict):
    # load content
    content = load_file_content(filename)

    # Skip tables of contents
    content_start = find_content_start(content)

    content = content[content_start:]

    # extract sections, assign text based on mapping_dict
    anchors = find_anchors(content)
    result = map_sections(content, anchors, mapping_dict)

    # assign metadata
    result["metadata"] = {"document_name": Path(filename).stem}
    return result


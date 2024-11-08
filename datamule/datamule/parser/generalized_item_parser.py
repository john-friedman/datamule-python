# Parses e.g. 10-K, 10-Q,..... any form with items and/or parts
from .helper import load_file_content, clean_title, clean_text
from pathlib import Path
import re

# OK figured out general pattern
# find toc
# figure out mapping. we do need it
# just do mapping tonight

pattern = re.compile(r'^\s*(?:item\s+\d+(?:\.\d+)?(?:[a-z])?|signature(?:\.?s)?)\s*', re.I | re.M)

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

# I think this works, but I haven't tested it extensively.
def map_sections(content, anchors):
    positions = anchors + [('end', len(content))]
    
    result = {}
    for i, (title, start) in enumerate(positions[:-1]):
        _, next_start = positions[i + 1]
        section_text = content[start:next_start].strip()
        result[title.lower()] = clean_text(section_text)
    
    def sort_key(x):
        match = re.search(r'item\s+(\d+)(?:[\.a-z])?', x[0], re.I)
        if not match:
            return float('inf')
        num = match.group(0).lower()
        # This will sort 1, 1a, 1b, 2, 2a etc
        return float(re.findall(r'\d+', num)[0]) + (ord(num[-1]) - ord('a') + 1) / 100 if num[-1].isalpha() else float(re.findall(r'\d+', num)[0])
        
    return dict(sorted(result.items(), key=sort_key))

# def find_content_start(anchors):
#     def find_first_non_repeating(seq):
#         for i in range(len(seq)):
#             remaining = seq[i:]
#             # Get same length subsequence from the next position
#             next_seq = seq[i + 1:i + 1 + len(remaining)]
#             if remaining != next_seq and len(next_seq) > 0:
#                 return i
#         return 0  # Default to start if no pattern found
    
#     return find_first_non_repeating([title for title, _ in anchors])

def generalized_parser(filename):
    # load content
    content = load_file_content(filename)

    # find anchors
    anchors = find_anchors(content)

    # Skip tables of contents. Not implemented yet, since we overwrite the keys anyway.
    # content_start = find_content_start(anchors)
    # print(content_start)

    result = {}
    # assign metadata
    result["metadata"] = {"document_name": Path(filename).stem}

    # extract sections, assign text based on mapping_dict
    result['document'] = map_sections(content, anchors)

    return result


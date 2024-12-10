from pathlib import Path
import re
from .helper import load_file_content, clean_title

PART_PATTERN = re.compile(r'\n\s*part[.:)?\s]+([IVX]+|\d+)', re.I)
ITEM_PATTERN = re.compile(r'\n\s*item[.:)?\s]+(\d+[A-Z]?)', re.I)
IS_10K_PATTERN = re.compile(r'item[.:)?\s]+14', re.I)
TOC_END_PATTERN = re.compile(r'(?:item[.:)?\s]+14).*?(?=\n\s*item[.:)?\s]+1\b)', re.I | re.DOTALL)

ROMAN_TO_NUM = {'I': '1', 'II': '2', 'III': '3', 'IV': '4'}

ITEM_TO_PART = {
   '1': 'I', '1A': 'I', '1B': 'I', '1C': 'I', '2': 'I', '3': 'I', '4': 'I',
   '5': 'II', '6': 'II', '7': 'II', '7A': 'II', '8': 'II', '9': 'II', '9A': 'II', '9B': 'II', '9C': 'II',
   '10': 'III', '11': 'III', '12': 'III', '13': 'III', '14': 'III',
   '15': 'IV', '16': 'IV', '16A': 'IV'
}

def find_content_start(content):
   toc_match = TOC_END_PATTERN.search(content)
   if toc_match:
       item_1_pattern = re.compile(r'\n\s*item\s*1\b', re.I)
       item_1_match = item_1_pattern.search(content, toc_match.end())
       if item_1_match:
           return item_1_match.start()
   return 0

def find_anchors(content):
   start_pos = find_content_start(content)
   content = '\n' + content[start_pos:]
   
   anchors = []
   for part_match in PART_PATTERN.finditer(content):
       anchors.append(('part', part_match.group(1), part_match.start() + start_pos, part_match.group()))
       
   for item_match in ITEM_PATTERN.finditer(content):
       anchors.append(('item', item_match.group(1), item_match.start() + start_pos, item_match.group()))
   
   return sorted(anchors, key=lambda x: x[2])

def extract_sections(content, anchors, filename):
    if not anchors:
        return {}
        
    result = {
        "metadata": {"document_name": Path(filename).stem},
        "document": {
            "part1": {}, "part2": {}, "part3": {}, "part4": {}
        }
    }
    
    last_item = None
    current_text = None
    
    for i, current in enumerate(anchors):
        if current[0] == 'item':
            next_pos = anchors[i+1][2] if i < len(anchors)-1 else len(content)
            text = content[current[2]:next_pos].strip()
            
            if current[1] == last_item:
                current_text += "\n\n" + text
            else:
                if last_item and last_item in ITEM_TO_PART:
                    part_num = ROMAN_TO_NUM[ITEM_TO_PART[last_item]]
                    result["document"][f"part{part_num}"][f"item{last_item.lower()}"] = current_text
                current_text = text
                last_item = current[1]
    
    if last_item and last_item in ITEM_TO_PART:
        part_num = ROMAN_TO_NUM[ITEM_TO_PART[last_item]]
        result["document"][f"part{part_num}"][f"item{last_item.lower()}"] = current_text
    
    # Only keep non-empty parts
    result["document"] = {k:v for k,v in result["document"].items() if v}
    return result

def parse_10k(filename):
   content = load_file_content(filename)
   if not IS_10K_PATTERN.search(content):
       return {}
   anchors = find_anchors(content)
   return extract_sections(content, anchors, filename)
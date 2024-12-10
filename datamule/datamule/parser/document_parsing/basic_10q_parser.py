from pathlib import Path
from .helper import load_file_content, clean_title
import re

PART_II_PATTERN = re.compile(r'\n\s*part\s+II\.?(?:[:\s\.]|$)', re.I)
ITEM_PATTERN = re.compile(r'\n\s*item\s+(\d+[A-Z]?)\.?(?:[:\s\.]|$)', re.I)
TOC_END_PATTERN = re.compile(r'(?:item\s*6\.?).*?(?=\n\s*item\s*1\.?\b)', re.I | re.DOTALL)

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
    
    part_ii_match = PART_II_PATTERN.search(content)
    part_ii_pos = part_ii_match.start() + start_pos if part_ii_match else None

    anchors = []
    for item_match in ITEM_PATTERN.finditer(content):
        anchors.append(('item', item_match.group(1), item_match.start() + start_pos, item_match.group()))
    
    return sorted(anchors, key=lambda x: x[2]), part_ii_pos

def extract_sections(content, anchors_and_part2, filename):
    anchors, part2_pos = anchors_and_part2
    if not anchors:
        return {}
        
    result = {
        "metadata": {"document_name": Path(filename).stem},
        "document": {
            "part1": {},
            "part2": {}
        }
    }
    
    last_item = None
    current_text = None
    last_pos = None
    
    for i, current in enumerate(anchors):
        next_pos = anchors[i+1][2] if i < len(anchors)-1 else len(content)
        
        if current[1] == last_item:
            current_text += "\n\n" + content[current[2]:next_pos].strip()
        else:
            if last_item is not None:
                part_key = "part2" if (part2_pos and last_pos >= part2_pos) else "part1"
                result["document"][part_key][f"item{last_item.lower()}"] = current_text
            
            current_text = content[current[2]:next_pos].strip()
            last_item = current[1]
            last_pos = current[2]
    
    if last_item is not None:
        part_key = "part2" if (part2_pos and last_pos >= part2_pos) else "part1"
        result["document"][part_key][f"item{last_item.lower()}"] = current_text
    
    # Clean empty parts
    result["document"] = {k:v for k,v in result["document"].items() if v}
    return result

def parse_10q(filename):
    content = load_file_content(filename)
    anchors_and_part2 = find_anchors(content)
    return extract_sections(content, anchors_and_part2, filename)
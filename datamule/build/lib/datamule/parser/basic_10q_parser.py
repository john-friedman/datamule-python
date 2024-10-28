from pathlib import Path
from selectolax.parser import HTMLParser
import re

PART_II_PATTERN = re.compile(r'\n\s*part\s+II\.?(?:[:\s\.]|$)', re.I)
ITEM_PATTERN = re.compile(r'\n\s*item\s+(\d+[A-Z]?)\.?(?:[:\s\.]|$)', re.I)
TOC_END_PATTERN = re.compile(r'(?:item\s*6\.?).*?(?=\n\s*item\s*1\.?\b)', re.I | re.DOTALL)

def load_file_content(filename):
    path = Path(filename)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        return HTMLParser(content).text() if path.suffix.lower() in {'.html', '.htm'} else content

def clean_title(title):
    return title.strip()

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
    
    # Find Part II position after TOC
    part_ii_match = PART_II_PATTERN.search(content)
    part_ii_pos = part_ii_match.start() + start_pos if part_ii_match else None

    anchors = []
    for item_match in ITEM_PATTERN.finditer(content):
        anchors.append(('item', item_match.group(1), item_match.start() + start_pos, item_match.group()))
    
    # Remove the second addition of start_pos
    return sorted(anchors, key=lambda x: x[2]), part_ii_pos  # Just return part_ii_pos without adding start_pos again

def extract_sections(content, anchors_and_part2, filename):
    anchors, part2_pos = anchors_and_part2
    if not anchors:
        return {}
        
    result = {
        "document_name": Path(filename).stem,
        "content": [
            {"title": "PART I", "items": []},
            {"title": "PART II", "items": []}
        ]
    }
    
    last_item = None
    current_text = None
    current_title = None
    
    for i, current in enumerate(anchors):
        next_pos = anchors[i+1][2] if i < len(anchors)-1 else len(content)
        
        if current[1] == last_item:  # Sequential match - merge
            current_text += "\n\n" + content[current[2]:next_pos].strip()
        else:  # New item
            if last_item is not None:
                item_dict = {
                    "title": current_title,
                    "text": current_text
                }
                # Use the CURRENT item's position for classification, not the next one
                part_idx = 1 if (part2_pos and last_pos >= part2_pos) else 0
                result["content"][part_idx]["items"].append(item_dict)
            
            current_text = content[current[2]:next_pos].strip()
            current_title = clean_title(current[3])
            last_item = current[1]
            last_pos = current[2]  # Store the current position for next iteration
    
    # Add the last section
    if last_item is not None:
        item_dict = {
            "title": current_title,
            "text": current_text
        }
        # Use the last stored position
        part_idx = 1 if (part2_pos and last_pos >= part2_pos) else 0
        result["content"][part_idx]["items"].append(item_dict)
    
    return result

def parse_10q(filename):
    content = load_file_content(filename)
    anchors_and_part2 = find_anchors(content)
    return extract_sections(content, anchors_and_part2, filename)
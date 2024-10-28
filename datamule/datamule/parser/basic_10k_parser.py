from pathlib import Path
from selectolax.parser import HTMLParser
import re

PART_PATTERN = re.compile(r'\n\s*part\s+([IVX]+|\d+)', re.I)
ITEM_PATTERN = re.compile(r'\n\s*item\s+(\d+[A-Z]?)', re.I)
IS_10K_PATTERN = re.compile(r'item\s*14', re.I)
TOC_END_PATTERN = re.compile(r'(?:item\s*14).*?(?=\n\s*item\s*1\b)', re.I | re.DOTALL)

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
        "document_name": Path(filename).stem,
        "content": []
    }
    
    last_item = None
    current_text = None
    current_title = None
    
    for i, current in enumerate(anchors):
        if current[0] == 'item':
            next_pos = anchors[i+1][2] if i < len(anchors)-1 else len(content)
            text = content[current[2]:next_pos].strip()
            
            if current[1] == last_item:  # Sequential match - merge
                current_text += "\n\n" + text
            else:  # New item - save previous if exists and start new
                if last_item is not None:
                    result["content"].append({
                        "title": current_title,
                        "text": current_text
                    })
                current_text = text
                current_title = clean_title(current[3])
                last_item = current[1]
    
    # Don't forget to add the last section
    if last_item is not None:
        result["content"].append({
            "title": current_title,
            "text": current_text
        })
    
    return result

def parse_10k(filename):
    content = load_file_content(filename)
    if not IS_10K_PATTERN.search(content):
        return {}
    anchors = find_anchors(content)
    return extract_sections(content, anchors, filename)
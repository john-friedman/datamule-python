from pathlib import Path
from selectolax.parser import HTMLParser
import re

PART_PATTERN = re.compile(
    r"(?:^[ \t]*)"
    r"(?:PART\s+(?:I|II|III|IV))",
    re.IGNORECASE | re.MULTILINE
)

ITEM_PATTERN = re.compile(
    r"(?:^[ \t]*)"
    r"(?:Item|ITEM)\s*"
    r"(?:"
    r"15|"
    r"14|"
    r"13|"
    r"12|"
    r"11|"
    r"10|"
    r"9B|"
    r"9A|"
    r"9|"
    r"8|"
    r"7|"
    r"6|"
    r"5|"
    r"4|"
    r"3D|"
    r"3C|"
    r"3B|"
    r"3A|"
    r"3|"
    r"2F|"
    r"2E|"
    r"2D|"
    r"2C|"
    r"2B|"
    r"2A|"
    r"2|"
    r"1B|"
    r"1A|"
    r"1"
    r")",
    re.IGNORECASE | re.MULTILINE
)

SIGNATURES_PATTERN = re.compile(
    r"^[ \t]*SIGNATURES?[\.|\s|\d]*$",
    re.IGNORECASE | re.MULTILINE
)

ITEM8_PATTERN = re.compile(
    r"^[ \t]*(?:Item|ITEM)\s*8",
    re.IGNORECASE | re.MULTILINE
)

ITEM1_6_PATTERN = re.compile(
    r"^[ \t]*(?:Item|ITEM)\s*(?:1|6)(?:\s|$)",
    re.IGNORECASE | re.MULTILINE
)

WHITESPACE_PATTERN = re.compile(r'\s+')

def load_file_content(filename: Path) -> str:
    path = Path(filename)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        return HTMLParser(content).text() if path.suffix.lower() in {'.html', '.htm'} else content

def clean_title(title: str) -> str:
    return ' '.join(title.replace('\n', ' ').split()).upper()

def parse_section(text: str, start: int, end: int) -> str:
    return WHITESPACE_PATTERN.sub(' ', text[start:end].strip())

def parse_10kq(filename: Path) -> dict:
    text = load_file_content(filename)
    document_name = Path(filename).stem
    
    sig_matches = list(SIGNATURES_PATTERN.finditer(text))
    if len(sig_matches) > 1:
        text = text[sig_matches[0].end():]
    else:
        # If no multiple signatures, try Item 8 detection
        item8_matches = list(ITEM8_PATTERN.finditer(text))
        if item8_matches:
            first_item8_pos = item8_matches[0].start()
            # Look for Item 1 or 6 AFTER the first Item 8
            item1_6_matches = list(ITEM1_6_PATTERN.finditer(text[first_item8_pos:]))
            if item1_6_matches:
                # First Item 8 was in TOC, skip to the Item 1/6 we found
                text = text[first_item8_pos + item1_6_matches[0].start():]
    
    section_matches = list(PART_PATTERN.finditer(text))
    item_matches = list(ITEM_PATTERN.finditer(text))
    
    if not section_matches:
        return {'document_name': document_name, 'content': []}
    
    content = []
    for i, section_match in enumerate(section_matches):
        section_start = section_match.start()
        section_end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(text)
        
        section_title = clean_title(section_match.group())
        section_items = []
        
        section_items_matches = [
            m for m in item_matches 
            if section_start <= m.start() < section_end
        ]
        
        for j, item_match in enumerate(section_items_matches):
            item_start = item_match.start()
            item_end = section_items_matches[j + 1].start() if j + 1 < len(section_items_matches) else section_end
            
            item_title = clean_title(item_match.group())
            item_text = parse_section(text, item_start, item_end)
            
            if item_text:
                section_items.append({
                    'title': item_title,
                    'text': item_text
                })
        
        if section_items:
            content.append({
                'title': section_title,
                'content': section_items
            })
    
    return {'document_name': document_name, 'content': content}
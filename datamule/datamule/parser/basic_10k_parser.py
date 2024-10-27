from pathlib import Path
from selectolax.parser import HTMLParser
import re
from collections import defaultdict

PART_PATTERN = re.compile(
    r"(?:^[ \t]*)"
    r"(?:PART\s+(?:I|II|III|IV|F/S)|SIGNATURES?)",
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

# Item to Part mappings
ITEM_TO_PART_10K = {
    1: "PART I",
    2: "PART I",
    3: "PART II",
    4: "PART II",
    5: "PART III",
    6: "PART III",
    7: "PART III",
    8: "PART III",
    9: "PART III",
    "9A": "PART III",
    "9B": "PART III",
    10: "PART III",
    11: "PART III",
    12: "PART III",
    13: "PART III",
    14: "PART III",
    15: "PART IV"
}

# 10-KSB has a different structure
ITEM_TO_PART_10KSB = {
    1: "PART I",
    2: "PART I",
    3: "PART II",
    4: "PART II",
    5: "PART II",
    6: "PART II",
    7: "PART III",
    8: "PART III",
    # Financial Statement Items map to Part F/S
    "1F": "PART F/S",
    "2F": "PART F/S"
}

def load_file_content(filename: Path) -> str:
    path = Path(filename)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        return HTMLParser(content).text() if path.suffix.lower() in {'.html', '.htm'} else content

def clean_title(title: str) -> str:
    return ' '.join(title.replace('\n', ' ').split()).upper()

def parse_section(text: str, start: int, end: int) -> str:
    lines = text[start:end].strip().split('\n')
    cleaned_lines = [' '.join(line.split()) for line in lines]
    return '\n'.join(line for line in cleaned_lines if line)

def get_item_number(item_match):
    """Extract the item number, handling special cases like 9A, 9B, etc."""
    text = item_match.group().upper()
    # Check for special items first
    for special in ["9B", "9A", "3D", "3C", "3B", "3A", "2F", "2E", "2D", "2C", "2B", "2A", "1B", "1A"]:
        if f"ITEM {special}" in text or f"ITEM{special}" in text:
            return special
    # Then check for numeric items
    for num in ["15", "14", "13", "12", "11", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1"]:
        if f"ITEM {num}" in text or f"ITEM{num}" in text:
            return int(num)
    return None

def find_content_start(text: str, item_matches: list) -> tuple[int, bool]:
    """Determine if it's a 10-K or 10-KSB and find content start."""
    # Check for Item 14 to identify 10-K
    is_10k = any(get_item_number(m) == 14 for m in item_matches)
    
    # Convert matches to a list of (position, item_number, text_length) tuples
    items_info = []
    for i, match in enumerate(item_matches):
        start_pos = match.start()
        end_pos = item_matches[i + 1].start() if i + 1 < len(item_matches) else len(text)
        item_num = get_item_number(match)
        text_length = end_pos - start_pos
        if item_num is not None:
            items_info.append((start_pos, item_num, text_length))
    
    if is_10k:
        print("10-K")
        # Find sequences of items with short text between them (TOC)
        toc_sequences = []
        current_sequence = []
        
        for i, (pos, item_num, text_length) in enumerate(items_info):
            if not current_sequence:
                current_sequence.append((pos, item_num))
            else:
                # If text between items is short (likely TOC) and items are on same or adjacent lines
                prev_pos = current_sequence[-1][0]
                lines_between = text[prev_pos:pos].count('\n')
                if text_length < 500 and lines_between <= 3:  # Adjust these thresholds as needed
                    current_sequence.append((pos, item_num))
                else:
                    if len(current_sequence) >= 3:  # Found a TOC sequence
                        toc_sequences.append(current_sequence)
                    current_sequence = [(pos, item_num)]
        
        if current_sequence and len(current_sequence) >= 3:
            toc_sequences.append(current_sequence)
        
        # Find the last TOC sequence that contains Item 14
        last_toc_end = 0
        for sequence in toc_sequences:
            if any(item_num == 14 for _, item_num in sequence):
                last_toc_end = sequence[-1][0]
        
        if last_toc_end > 0:
            # Find first Item 1 after last TOC that has substantial text following it
            for pos, item_num, text_length in items_info:
                if pos > last_toc_end and item_num == 1 and text_length > 500:  # Adjust threshold as needed
                    return pos, True
        
        # If no TOC found or no suitable Item 1, return start of document
        return 0, True
    
    else:
        print("10-KSB")
        # Similar logic for 10-KSB but look for its specific sequence pattern
        sequences = []
        current_sequence = []
        
        for i, (pos, item_num, text_length) in enumerate(items_info):
            if not current_sequence:
                current_sequence.append((pos, item_num))
            else:
                prev_pos = current_sequence[-1][0]
                lines_between = text[prev_pos:pos].count('\n')
                if text_length < 500 and lines_between <= 3:  # Adjust these thresholds as needed
                    current_sequence.append((pos, item_num))
                else:
                    if len(current_sequence) >= 5:  # Need enough items to identify TOC
                        sequences.append(current_sequence)
                    current_sequence = [(pos, item_num)]
        
        if current_sequence and len(current_sequence) >= 5:
            sequences.append(current_sequence)
        
        # Look for the characteristic 10-KSB sequence
        for sequence in sequences:
            # Convert sequence to just item numbers
            seq_numbers = [item_num for _, item_num in sequence if isinstance(item_num, int)]
            
            # Check if sequence matches expected pattern
            # We're looking for combinations of items 1-8 appearing close together
            unique_items = set(seq_numbers)
            if len(unique_items) >= 5 and all(num <= 8 for num in unique_items):
                sequence_end = sequence[-1][0]
                
                # Find first Item 1 after sequence that has substantial text
                for pos, item_num, text_length in items_info:
                    if pos > sequence_end and item_num == 1 and text_length > 500:  # Adjust threshold as needed
                        return pos, False
        
        return 0, False

def collect_items(text: str, start_pos: int, item_matches: list) -> list:
    """Collect all items and their text."""
    items = []
    
    # Filter matches to only those after start_pos
    valid_matches = [m for m in item_matches if m.start() >= start_pos]
    
    for i, match in enumerate(valid_matches):
        item_start = match.start()
        item_end = valid_matches[i + 1].start() if i + 1 < len(valid_matches) else len(text)
        
        item_num = get_item_number(match)
        if item_num is not None:
            items.append({
                'number': item_num,
                'title': clean_title(match.group()),
                'text': parse_section(text, item_start, item_end),
                'position': item_start
            })
    
    return items

def build_document_structure(items: list, is_10k: bool) -> list:
    """Build document structure based on items."""
    # Use appropriate mapping based on document type
    item_mapping = ITEM_TO_PART_10K if is_10k else ITEM_TO_PART_10KSB
    
    # Group items by part
    parts_dict = defaultdict(lambda: {'text': '', 'items': []})
    
    for item in items:
        item_num = item['number']
        if item_num in item_mapping:
            part_name = item_mapping[item_num]
            parts_dict[part_name]['items'].append({
                'title': item['title'],
                'text': item['text']
            })
    
    # Convert to list format
    content = []
    
    # Define part order
    if is_10k:
        part_order = ["PART I", "PART II", "PART III", "PART IV", "SIGNATURES"]
    else:
        part_order = ["PART I", "PART II", "PART III", "PART F/S", "SIGNATURES"]
    
    # Build content in correct order, only including parts that have items
    for part_name in part_order:
        if part_name in parts_dict and parts_dict[part_name]['items']:
            content.append({
                'title': part_name,
                'text': parts_dict[part_name]['text'],
                'content': parts_dict[part_name]['items']
            })
    
    return content

def parse_10k(filename: Path) -> dict:
    """Main parsing function."""
    text = load_file_content(filename)
    document_name = Path(filename).stem
    
    # Get all potential matches
    item_matches = list(ITEM_PATTERN.finditer(text))
    
    if not item_matches:
        return {'document_name': document_name, 'content': []}
    
    # Find content start and determine document type
    content_start, is_10k = find_content_start(text, item_matches)
    
    # Collect all items
    items = collect_items(text, content_start, item_matches)
    
    # Build document structure
    content = build_document_structure(items, is_10k)
    
    return {'document_name': document_name, 'content': content}
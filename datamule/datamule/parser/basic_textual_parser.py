from pathlib import Path
from selectolax.parser import HTMLParser
import re

# Mostly AI Slop

def load_file_content(filename):
    ext = filename.lower().split('.')[-1]
    
    with open(filename, 'r', encoding='utf-8') as file:
        if ext in ['html', 'htm']:
            from selectolax.parser import HTMLParser
            return HTMLParser(file.read()).text()
        return file.read()

def parse_8k(filename):
    # load text
    text = load_file_content(filename)

    # Pattern for all items and signatures at start of line (with optional spaces)
    pattern = (
        r"(?:^[ \t]*)"  # Start of line with optional whitespace
        r"(?:"  # Start non-capturing group for entire pattern
        r"(?:Item|ITEM)\s*"  # Match "Item" or "ITEM" followed by whitespace
        r"(?:"  # Start non-capturing group for item numbers
        r"1\.0[1-4]|"  # Section 1
        r"2\.0[1-6]|"  # Section 2
        r"3\.0[1-3]|"  # Section 3
        r"4\.0[1-2]|"  # Section 4
        r"5\.0[1-8]|"  # Section 5
        r"6\.0[1-5]|"  # Section 6
        r"7\.01|"      # Section 7
        r"8\.01|"      # Section 8
        r"9\.01"       # Section 9
        r")"
        r"|"           # OR
        r"SIGNATURES?" # Match SIGNATURE or SIGNATURES
        r")"          # End main non-capturing group
    )
    
    # Find all matches with their positions using MULTILINE flag
    matches = []
    for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
        matches.append((match.group().strip(), match.start()))
    
    # Extract text between matches
    sections = {}
    document_name = Path(filename).stem  # Get filename without extension
    sections[document_name] = {"content": {}}
    
    for i in range(len(matches) - 1):
        current_item = matches[i][0].upper()
        start_pos = matches[i][1] + len(matches[i][0])  # Use original match length
        end_pos = matches[i + 1][1]
        
        # Clean the extracted text
        section_text = text[start_pos:end_pos].strip()
        section_text = re.sub(r'\s+', ' ', section_text)  # Normalize whitespace
        
        # Skip empty sections
        if section_text:
            sections[document_name]["content"][current_item] = {
                "title": current_item,
                "text": section_text
            }
    
    # Handle the last section (up to end of text)
    if matches:
        last_item = matches[-1][0].upper()
        last_start = matches[-1][1] + len(matches[-1][0])
        last_text = text[last_start:].strip()
        last_text = re.sub(r'\s+', ' ', last_text)
        if last_text:
            sections[document_name]["content"][last_item] = {
                "title": last_item,
                "text": last_text
            }
    
    return sections
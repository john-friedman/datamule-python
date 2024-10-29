from pathlib import Path
import re
from .helper import load_file_content, clean_title

PART_PATTERN = re.compile(r'\n\s*part[.:)?\s]+([IVX]+|\d+)', re.I)
ITEM_PATTERN = re.compile(r'\n\s*item[.:)?\s]+(\d+[A-Z]?)', re.I)
IS_10K_PATTERN = re.compile(r'item[.:)?\s]+14', re.I)
TOC_END_PATTERN = re.compile(r'(?:item[.:)?\s]+14).*?(?=\n\s*item[.:)?\s]+1\b)', re.I | re.DOTALL)

# Mapping of items to their respective parts
# Mapping of SEC Form 10-K items to their respective parts
ITEM_TO_PART = {
    # Part I
    '1': 'I',      # Business
    '1A': 'I',     # Risk Factors
    '1B': 'I',     # Unresolved Staff Comments
    '1C': 'I',     # Cybersecurity
    '2': 'I',      # Properties
    '3': 'I',      # Legal Proceedings
    '4': 'I',      # Mine Safety Disclosures
    
    # Part II
    '5': 'II',     # Market for Registrant's Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities
    '6': 'II',     # [Reserved]
    '7': 'II',     # Management's Discussion and Analysis of Financial Condition and Results of Operations
    '7A': 'II',    # Quantitative and Qualitative Disclosures About Market Risk
    '8': 'II',     # Financial Statements and Supplementary Data
    '9': 'II',     # Changes in and Disagreements with Accountants on Accounting and Financial Disclosure
    '9A': 'II',    # Controls and Procedures
    '9B': 'II',    # Other Information
    '9C': 'II',    # Disclosure Regarding Foreign Jurisdictions that Prevent Inspections
    
    # Part III
    '10': 'III',   # Directors, Executive Officers and Corporate Governance
    '11': 'III',   # Executive Compensation
    '12': 'III',   # Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters
    '13': 'III',   # Certain Relationships and Related Transactions, and Director Independence
    '14': 'III',   # Principal Accountant Fees and Services
    
    # Part IV
    '15': 'IV',    # Exhibit and Financial Statement Schedules
    '16': 'IV',    # Form 10-K Summary
    '16A': 'IV',   # Disclosure Regarding Foreign Jurisdictions that Prevent Inspections
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
        "document_name": Path(filename).stem,
        "content": []
    }
    
    # Initialize structure with parts
    parts = {
        'I': {'title': 'PART I', 'items': []},
        'II': {'title': 'PART II', 'items': []},
        'III': {'title': 'PART III', 'items': []},
        'IV': {'title': 'PART IV', 'items': []}
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
                if last_item is not None and last_item in ITEM_TO_PART:
                    part = ITEM_TO_PART[last_item]
                    parts[part]['items'].append({
                        "title": current_title,
                        "text": current_text
                    })
                current_text = text
                current_title = clean_title(current[3])
                last_item = current[1]
    
    # Don't forget to add the last section
    if last_item is not None and last_item in ITEM_TO_PART:
        part = ITEM_TO_PART[last_item]
        parts[part]['items'].append({
            "title": current_title,
            "text": current_text
        })
    
    # Add only non-empty parts to the result
    result["content"] = [part_data for part_data in parts.values() if part_data['items']]
    
    return result

def parse_10k(filename):
    content = load_file_content(filename)
    if not IS_10K_PATTERN.search(content):
        return {}
    anchors = find_anchors(content)
    return extract_sections(content, anchors, filename)
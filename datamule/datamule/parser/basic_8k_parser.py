from pathlib import Path
from selectolax.parser import HTMLParser
import re
from collections import defaultdict

# Pre-compile regex pattern with flags
ITEM_PATTERN = re.compile(
    r"(?:^[ \t]*)"
    r"(?:"
    r"(?:Item|ITEM)\s*"
    r"(?:"
    r"1\.0[1-4]|"
    r"2\.0[1-6]|"
    r"3\.0[1-3]|"
    r"4\.0[1-2]|"
    r"5\.0[1-8]|"
    r"6\.0[1-5]|"
    r"7\.01|"
    r"8\.01|"
    r"9\.01"
    r")"
    r"|"
    r"SIGNATURES?"
    r")",
    re.IGNORECASE | re.MULTILINE
)

# Pre-compile whitespace normalization pattern
WHITESPACE_PATTERN = re.compile(r'\s+')

class DuplicateSectionError(Exception):
    """Raised when a section appears multiple times before a different section."""
    pass

def load_file_content(filename: Path) -> str:
    """Load and parse file content based on extension."""
    path = Path(filename)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        return HTMLParser(content).text() if path.suffix.lower() in {'.html', '.htm'} else content

def clean_title(title: str) -> str:
    """Clean up section title by removing newlines and normalizing whitespace."""
    return ' '.join(title.replace('\n', ' ').split())

def parse_section(text: str, start: int, end: int) -> str:
    """Parse and clean a section of text."""
    return WHITESPACE_PATTERN.sub(' ', text[start:end].strip())

def validate_section_sequence(matches: list) -> None:
    """
    Validate that no section appears multiple times before a different section.
    
    Args:
        matches: List of tuples containing (section_title, start_position)
    
    Raises:
        DuplicateSectionError: If a section appears multiple times before a different section
    """
    current_section = None
    current_base = None
    
    for match, _ in matches:
        # Extract base section number (e.g., "ITEM 5.02" from "ITEM 5.02 CONTINUED")
        base_section = re.match(r'(?:Item|ITEM)\s*(?:\d+\.\d+|\bSIGNATURES?\b)', match)
        if base_section:
            base_section = base_section.group().upper()
            
            if current_base is None:
                current_base = base_section
            elif base_section != current_base:
                # Different section encountered, reset tracking
                current_base = base_section
            else:
                # Same base section encountered before a different section
                raise DuplicateSectionError(
                    f"Section {base_section} appears multiple times before a different section"
                )

def parse_8k(filename: Path) -> dict:
    """
    Parse 8-K document and extract sections.
    
    Raises:
        DuplicateSectionError: If a section appears multiple times before a different section
    """
    text = load_file_content(filename)
    document_name = Path(filename).stem
    
    # Get all matches at once
    matches = [(clean_title(m.group().strip()), m.start()) for m in ITEM_PATTERN.finditer(text)]
    if not matches:
        return {'document_name': document_name, "content": []}
    
    # Validate section sequence
    validate_section_sequence(matches)
    
    # Pre-calculate section boundaries
    sections_data = []
    for i, (current_match, start_pos) in enumerate(matches[:-1]):
        sections_data.append((
            current_match.upper(),
            start_pos,
            matches[i + 1][1]
        ))
    
    # Add last section
    last_match, last_pos = matches[-1]
    sections_data.append((
        last_match.upper(),
        last_pos,
        len(text)
    ))
    
    # Build sections list using list comprehension
    content = [
        {
            "title": title,
            "text": section_text
        }
        for title, start, end in sections_data
        if (section_text := parse_section(text, start, end))
    ]
    
    return {'document_name':document_name, "content": content}
import re
from pathlib import Path
from .helper import load_file_content, clean_title

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

WHITESPACE_PATTERN = re.compile(r'\s+')

def parse_section(text: str, start: int, end: int) -> str:
   return WHITESPACE_PATTERN.sub(' ', text[start:end].strip())

def validate_section_sequence(matches: list) -> None:
   current_base = None
   
   for match, _ in matches:
       base_section = re.match(r'(?:Item|ITEM)\s*(?:\d+\.\d+|\bSIGNATURES?\b)', match)
       if base_section:
           base_section = base_section.group().upper()
           
           if current_base is None:
               current_base = base_section
           elif base_section != current_base:
               current_base = base_section
           else:
               raise DuplicateSectionError(f"Section {base_section} appears multiple times before a different section")

def parse_8k(filename: Path) -> dict:
   text = load_file_content(filename)
   matches = [(clean_title(m.group().strip()), m.start()) for m in ITEM_PATTERN.finditer(text)]
   
   result = {
       "metadata": {"document_name": Path(filename).stem},
       "document": {}
   }
   
   if not matches:
       return result
   
   validate_section_sequence(matches)
   
   # Process all sections except last
   for i, (current_match, start_pos) in enumerate(matches[:-1]):
       section_text = parse_section(text, start_pos, matches[i + 1][1])
       if section_text:
            if "signature" in current_match.lower():
                key = "signatures" 
            else:
                key = f"item{current_match.lower().replace('item', '').strip()}"
            result["document"][key] = section_text
   
   # Process last section
   last_match, last_pos = matches[-1]
   section_text = parse_section(text, last_pos, len(text))
   if section_text:
        if "signature" in last_match.lower():
            key = "signatures" 
        else:
            key = f"item{last_match.lower().replace('item', '').strip()}"
        result["document"][key] = section_text
    
   return result

class DuplicateSectionError(Exception):
   """Raised when a section appears multiple times before a different section."""
   pass
import re
from pathlib import Path
from .helper import load_file_content, clean_title

ITEM_PATTERN_13G = re.compile(
    r"(?:^[ \t]*)"
    r"(?:"
    r"(?:Item|ITEM)\s*"
    r"(?:"
    r"10|"  # Move 10 to the start so it's matched before 1
    r"11|"  # Similarly with 11 and 12
    r"12|"
    r"1|"
    r"2|"
    r"3|"
    r"4|"
    r"5|"
    r"6|"
    r"7|"
    r"8|"
    r"9"
    r")"
    r"|"
    r"SIGNATURES?"
    r")",
    re.IGNORECASE | re.MULTILINE
)

def parse_13g(filename: Path) -> dict:
   text = load_file_content(filename)
   matches = [(clean_title(m.group().strip()), m.start()) for m in ITEM_PATTERN_13G.finditer(text)]
   
   result = {
       "metadata": {"document_name": Path(filename).stem},
       "document": {}
   }
   
   if not matches:
       return result
   
   for i, (current_match, start_pos) in enumerate(matches[:-1]):
       section_text = WHITESPACE_PATTERN.sub(' ', text[start_pos:matches[i + 1][1]]).strip()
       if section_text:
            if "signature" in current_match.lower():
                key = "signatures" 
            else:
                key = f"item{current_match.lower().replace('item', '').strip()}"
            result["document"][key] = section_text
   
   last_match, last_pos = matches[-1]
   section_text = WHITESPACE_PATTERN.sub(' ', text[last_pos:len(text)]).strip()
   if section_text:
        if "signature" in last_match.lower():
            key = "signatures" 
        else:
            key = f"item{last_match.lower().replace('item', '').strip()}"
        result["document"][key] = section_text
   
   return result

WHITESPACE_PATTERN = re.compile(r'\s+')
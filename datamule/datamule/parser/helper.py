
from selectolax.parser import HTMLParser
from pathlib import Path
def load_file_content(filename: Path) -> str:
    """Load and parse file content based on extension, normalizing only spaces and quotes."""
    path = Path(filename)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        content = HTMLParser(content).text() if path.suffix.lower() in {'.html', '.htm'} else content
        
        # Replace various space characters with regular space
        content = content.replace('\xa0', ' ').replace('\u2003', ' ')
        
        # Normalize quotes to standard ASCII quotes
        quotes_map = {
            '\u2018': "'",  # left single quote
            '\u2019': "'",  # right single quote
            '\u201c': '"',  # left double quote
            '\u201d': '"',  # right double quote
        }
        for old, new in quotes_map.items():
            content = content.replace(old, new)
            
        return content
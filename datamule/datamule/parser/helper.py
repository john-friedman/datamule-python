from selectolax.parser import HTMLParser
from pathlib import Path

from selectolax.parser import HTMLParser
from pathlib import Path

# Version 1: Direct text content from body
#2s
def load_content_v1(filename):
    parser = HTMLParser(open(filename).read())
    return parser.body.text(separator='\n', strip=True)

# Version 2: Using traverse with text nodes
#.36s
def load_content_v2(filename):
    parser = HTMLParser(open(filename).read())
    return '\n'.join(
        node.text_content.strip() 
        for node in parser.root.traverse(include_text=True)
        if node.text_content and node.text_content.strip()
    )



load_file_content = load_content_v2

# def load_file_content(filename):
#     path = Path(filename)
#     with open(path, 'r', encoding='utf-8') as file:
#         content = file.read()
        
#         if path.suffix.lower() in {'.html', '.htm'}:
#             parser = HTMLParser(content)
#             parser.strip_tags(['style', 'script', 'head'])  # Much faster than CSS selection
#             content = parser.text(deep=True, separator='\n', strip=True)
            
#         return content.translate(str.maketrans({
#             '\xa0': ' ', '\u2003': ' ',
#             '\u2018': "'", '\u2019': "'",
#             '\u201c': '"', '\u201d': '"'
#         }))
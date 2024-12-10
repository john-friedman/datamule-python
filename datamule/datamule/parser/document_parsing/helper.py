from selectolax.parser import HTMLParser
import re

# This will be modified in the future to remove SEC specific code such as <PAGE> tags
def load_text_content(filename):
    with open(filename) as f:
        return f.read().translate(str.maketrans({
            '\xa0': ' ', '\u2003': ' ',
            '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"'
        }))
    
def load_html_content(filename):
    parser = HTMLParser(open(filename).read())
    
    # Remove hidden elements first
    hidden_nodes = parser.css('[style*="display: none"], [style*="display:none"], .hidden, .hide, .d-none')
    for node in hidden_nodes:
        node.decompose()
    
    blocks = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section', 'li', 'td'}
    lines = []
    current_line = []
    
    def flush_line():
        if current_line:
            lines.append(' '.join(current_line))
            current_line.clear()
    
    for node in parser.root.traverse(include_text=True):
        if node.tag in ('script', 'style', 'css'):
            continue
            
        if node.tag in blocks:
            flush_line()
            lines.append('')
            
        if node.text_content:
            text = node.text_content.strip()
            if text:
                if node.tag in blocks:
                    flush_line()
                    lines.append(text)
                    lines.append('')
                else:
                    current_line.append(text)
    
    flush_line()
    
    text = '\n'.join(lines)
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')
    
    return text.translate(str.maketrans({
        '\xa0': ' ', '\u2003': ' ',
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"'
    }))
def load_file_content(filename):
    if filename.suffix =='.txt':
        return load_text_content(filename)
    elif filename.suffix in ['.html','.htm']:
        return load_html_content(filename)
    else:
        raise ValueError(f"Unsupported file type: {filename}")

def clean_title(title: str) -> str:
    """Clean up section title by removing newlines, periods, and all whitespace, converting to lowercase."""
    return ''.join(title.replace('\n', '').replace('.', '').split()).lower()

# This is a bit hacky, removes PART IV, PART V etc from the end of the text
# we do this to avoid having to map for general cases
def clean_text(text):
    text = text.strip()
    return re.sub(r'\s*PART\s+[IVX]+\s*$', '', text, flags=re.I)
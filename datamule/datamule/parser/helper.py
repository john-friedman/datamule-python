from selectolax.parser import HTMLParser
from pathlib import Path


def load_file_content(filename):
    #  ~ 30ms per file
    parser = HTMLParser(open(filename).read())
    text = '\n'.join(
        node.text_content.strip() 
        for node in parser.root.traverse(include_text=True)
        if node.text_content and node.text_content.strip()
    )
    return text.translate(str.maketrans({
        '\xa0': ' ', '\u2003': ' ',
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"'
    }))
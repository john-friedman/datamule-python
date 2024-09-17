import json
from lxml import etree

def create_interactive_html(data):
    # Create the root element (html)
    html = etree.Element("html")
    head = etree.SubElement(html, "head")
    body = etree.SubElement(html, "body")

    # Add CSS to the head
    style = etree.SubElement(head, "style")
    style.text = """
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: #ffffff;
            padding: 40px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1, h2, h3, h4 {
            color: #2c3e50;
            margin-top: 0;
        }
        h1 { font-size: 28px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { font-size: 24px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }
        h3 { font-size: 20px; }
        h4 { font-size: 18px; }
        .text {
            margin-bottom: 20px;
            font-size: 16px;
        }
        section {
            margin-bottom: 30px;
        }
        section section {
            margin-left: 20px;
        }
    """

    def process_content(content, parent_element, depth=0):
        for item in content:
            section = etree.SubElement(parent_element, "section")
            
            if 'title' in item and item['title']:
                title_tag = f"h{min(depth+1, 4)}"
                title_elem = etree.SubElement(section, title_tag)
                title_elem.text = item['title']
            
            if 'text' in item and item['text']:
                text_div = etree.SubElement(section, "div", attrib={"class": "text"})
                text_div.text = item['text']
            
            if 'content' in item:
                process_content(item['content'], section, depth + 1)

    # Create a container div
    container = etree.SubElement(body, "div", attrib={"class": "container"})

    # Start processing from the first item in the document
    start_dict = data['document'][0]['content'][0]
    process_content([start_dict], container)

    # Create an ElementTree object
    tree = etree.ElementTree(html)
    #return tree

    #Write the HTML to a file
    tree.write("executive_report.html", pretty_print=True, method="html", encoding="utf-8", doctype="<!DOCTYPE html>")
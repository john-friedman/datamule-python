
from lxml import etree
from .scripts import script1
from .styles import style1, style2

def create_interactive_html(data, path, script='script1', style='style1'):
    # Create the root element (html)
    html = etree.Element("html")
    head = etree.SubElement(html, "head")
    body = etree.SubElement(html, "body")

    # Add meta charset
    meta = etree.SubElement(head, "meta")
    meta.set("charset", "utf-8")

    # Add viewport meta tag for responsiveness
    viewport = etree.SubElement(head, "meta")
    viewport.set("name", "viewport")
    viewport.set("content", "width=device-width, initial-scale=1.0")

    # Add title
    title = etree.SubElement(head, "title")
    title.text = "Interactive Filing Viewer"

    # Add style
    style_elem = etree.SubElement(head, "style")
    if style == 'style1':
        style_elem.text = style1 
    elif style == 'style2':
        style_elem.text = style2
    
    # Add script
    script_elem = etree.SubElement(body, "script")
    if script == 'script1':
        script_elem.text = script1

    def process_content(content, parent_element, sidebar_list, depth=0):
        for item in content:
            section = etree.SubElement(parent_element, "section")
            
            if 'title' in item and item['title']:
                title_tag = f"h{min(depth+1, 4)}"
                title_elem = etree.SubElement(section, title_tag)
                title_elem.text = item['title']
                
                # Create an ID for the section
                section_id = item['title'].lower().replace(' ', '-')
                section.set('id', section_id)
                
                # Add link to sidebar
                li = etree.SubElement(sidebar_list, "li")
                a = etree.SubElement(li, "a", href=f"#{section_id}")
                a.text = item['title']
                
                if 'content' in item:
                    sub_ul = etree.SubElement(li, "ul")
                    process_content(item['content'], section, sub_ul, depth + 1)
            
            if 'text' in item and item['text']:
                text_div = etree.SubElement(section, "div", attrib={"class": "text"})
                text_div.text = item['text']

    # Create sidebar
    sidebar = etree.SubElement(body, "div", attrib={"class": "sidebar"})
    sidebar_title = etree.SubElement(sidebar, "div", attrib={"class": "sidebar-title"})
    sidebar_title.text = "Table of Contents"
    sidebar_ul = etree.SubElement(sidebar, "ul")

    # Create main content container
    main_content = etree.SubElement(body, "div", attrib={"class": "main-content"})

    # Start processing from the first item in the document
    start_dict = data['document'][0]['content'][0]
    process_content([start_dict], main_content, sidebar_ul)

    # Create an ElementTree object
    tree = etree.ElementTree(html)

    # Write the HTML to a file
    tree.write(path, pretty_print=True, method="html", encoding="utf-8", doctype="<!DOCTYPE html>")
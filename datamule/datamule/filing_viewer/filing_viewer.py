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
            margin: 0;
            padding: 0;
            display: flex;
            background-color: #f8f9fa;
        }
        .sidebar {
            width: 300px;
            height: 100vh;
            overflow-y: auto;
            background-color: #ffffff;
            padding: 30px;
            position: fixed;
            box-shadow: 0 0 20px rgba(0,0,0,0.05);
        }
        .main-content {
            margin-left: 360px;
            padding: 50px;
            max-width: 800px;
            background-color: #ffffff;
            box-shadow: 0 0 20px rgba(0,0,0,0.05);
            min-height: 100vh;
        }
        .sidebar ul {
            list-style-type: none;
            padding-left: 0;
        }
        .sidebar ul ul {
            padding-left: 20px;
        }
        .sidebar a {
            text-decoration: none;
            color: #495057;
            display: block;
            padding: 8px 0;
            transition: all 0.3s ease;
            font-size: 15px;
        }
        .sidebar a:hover {
            color: #007bff;
            padding-left: 5px;
        }
        .sidebar .active {
            font-weight: 600;
            color: #007bff;
        }
        h1, h2, h3, h4 {
            color: #212529;
            margin-top: 0;
            font-weight: 600;
        }
        h1 { 
            font-size: 32px; 
            border-bottom: 2px solid #007bff; 
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        h2 { 
            font-size: 24px; 
            border-bottom: 1px solid #dee2e6; 
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 20px;
        }
        h3 { font-size: 20px; margin-top: 30px; }
        h4 { font-size: 18px; margin-top: 25px; }
        .text {
            margin-bottom: 20px;
            font-size: 16px;
            color: #495057;
        }
        section {
            margin-bottom: 40px;
        }
        /* New styles for nested sections */
        section section {
            margin-left: 20px;
            border-left: 2px solid #e9ecef;
            padding-left: 20px;
        }
        section section section {
            margin-left: 15px;
        }
        section section section section {
            margin-left: 10px;
        }
        .sidebar-title {
            font-size: 24px;
            font-weight: 600;
            color: #212529;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #007bff;
        }
        @media (max-width: 1200px) {
            .sidebar {
                width: 250px;
            }
            .main-content {
                margin-left: 300px;
            }
        }
        @media (max-width: 992px) {
            body {
                flex-direction: column;
            }
            .sidebar {
                width: 100%;
                height: auto;
                position: static;
                padding: 20px;
            }
            .main-content {
                margin-left: 0;
                padding: 30px;
            }
        }
    """

    # Add JavaScript for scrollspy (unchanged)
    script = etree.SubElement(head, "script")
    script.text = """
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.sidebar a');
    const sidebar = document.querySelector('.sidebar');

    function makeActive(link) {
        navLinks.forEach(n => n.classList.remove('active'));
        link.classList.add('active');
    }

    function findActiveSection() {
        let currentSection = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= sectionTop - window.innerHeight / 2) {
                currentSection = section.getAttribute('id');
            }
        });
        return currentSection;
    }

    function updateSidebar() {
        const currentSection = findActiveSection();
        navLinks.forEach(link => {
            if (link.getAttribute('href').substring(1) === currentSection) {
                makeActive(link);
                // Center the active link in the sidebar
                const linkRect = link.getBoundingClientRect();
                const sidebarRect = sidebar.getBoundingClientRect();
                const targetScrollTop = link.offsetTop - sidebar.offsetTop - (sidebarRect.height / 2) + (linkRect.height / 2);
                sidebar.scrollTop = targetScrollTop;
            }
        });
    }

    window.addEventListener('scroll', updateSidebar);
    updateSidebar(); // Call once to set initial state
});
    """

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
    tree.write("executive_report.html", pretty_print=True, method="html", encoding="utf-8", doctype="<!DOCTYPE html>")

# Example usage:
# with open('your_json_file.json', 'r') as f:
#     data = json.load(f)
# create_interactive_html(data)
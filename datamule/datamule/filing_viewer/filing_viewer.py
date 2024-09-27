
# AI generated slop. Quick workaround to get mulebot server artifact to build correctly. Will rewrite later.
import re

def create_valid_id(title):
    # Remove any characters that are not alphanumeric, hyphen, underscore, colon, or period
    valid_id = re.sub(r'[^\w\-.:]+', '-', title)
    # Ensure the id starts with a letter
    if not valid_id[0].isalpha():
        valid_id = 'section-' + valid_id
    # Convert to lowercase
    return valid_id.lower()

def create_content(content, level=1):
    html = ""
    for index, item in enumerate(content):
        if 'title' in item:
            section_id = create_valid_id(item['title'])
        else:
            section_id = f'section-{level}-{index}'
        
        html += f'<div class="section level-{level}" id="{section_id}">'
        
        if 'title' in item:
            html += f'<h3 class="section-title">{item["title"]}</h3>'
        if 'text' in item:
            html += f'<p class="section-text">{item["text"]}</p>'
        
        if 'content' in item:
            html += '<div class="sub-content">'
            html += create_content(item['content'], level + 1)
            html += '</div>'
        
        html += '</div>'
    
    return html

def json_to_html(data):
    html = '<div class="dashboard-container">'
    
    # Sidebar
    html += '''
    <div class="sidebar" id="sidebar">
        <h2 class="sidebar-title">Sections</h2>
        <ul id="section-list" class="nav flex-column"></ul>
    </div>
    '''
    
    # Main content
    html += '<div class="main-content">'
    
    # Header
    html += f'''
    <header class="dashboard-header">
        <h1 class="dashboard-title">Filing Viewer</h1>
        <p class="dashboard-subtitle">CIK: {data['cik']} | Accession Number: {data['accession_number']}</p>
    </header>
    '''
    
    # Document content
    for doc in data['document']:
        if 'content' in doc:
            html += create_content(doc['content'])
    
    html += '</div></div>'
    
    return html

def create_interactive_filing(json_data):
    html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SEC 10-K Premium Executive Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
    <style>
        :root {{
            --primary-color: #333;
            --secondary-color: #666;
            --background-color: #f8f8f8;
            --text-color: #333;
            --border-color: #e0e0e0;
        }}
        body {{
            font-family: 'Arial', sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }}
        .dashboard-container {{
            display: flex;
            min-height: 100vh;
        }}
        .sidebar {{
            width: 250px;
            background-color: white;
            border-right: 1px solid var(--border-color);
            padding: 20px;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            transition: transform 0.3s ease-in-out;
        }}
        .main-content {{
            flex-grow: 1;
            margin-left: 250px;
            padding: 40px;
        }}
        .dashboard-header {{
            margin-bottom: 40px;
        }}
        .dashboard-title {{
            color: var(--primary-color);
            font-weight: bold;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        .dashboard-subtitle {{
            color: var(--secondary-color);
            font-size: 1rem;
        }}
        .section {{
            margin-bottom: 30px;
            padding-left: 20px;
            border-left: 2px solid var(--border-color);
        }}
        .section-title {{
            color: var(--primary-color);
            font-size: 1.5rem;
            margin-bottom: 15px;
        }}
        .level-2 {{ margin-left: 20px; }}
        .level-3 {{ margin-left: 40px; }}
        .nav-link {{
            color: var(--text-color);
            transition: all 0.3s ease;
            padding: 5px 10px;
            margin-bottom: 5px;
            border-radius: 4px;
        }}
        .nav-link:hover, .nav-link.active {{
            background-color: var(--background-color);
            color: var(--primary-color);
        }}
        .sidebar-title {{
            font-size: 1.2rem;
            color: var(--primary-color);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
        }}
        .toggle-sidebar {{
            display: none;
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 1000;
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
        }}
        @media (max-width: 768px) {{
            .sidebar {{
                transform: translateX(-100%);
                z-index: 1000;
            }}
            .sidebar.active {{
                transform: translateX(0);
            }}
            .main-content {{
                margin-left: 0;
                padding: 20px;
            }}
            .toggle-sidebar {{
                display: block;
            }}
            .dashboard-title {{
                font-size: 2rem;
            }}
            .section {{
                padding-left: 10px;
            }}
            .level-2, .level-3 {{
                margin-left: 10px;
            }}
        }}
    </style>
</head>
<body>
    <button class="toggle-sidebar" id="toggleSidebar">☰</button>
    {json_to_html(json_data)}
    <script>
        document.addEventListener('DOMContentLoaded', (event) => {{
            const sidebar = document.getElementById('sidebar');
            const toggleSidebar = document.getElementById('toggleSidebar');
            const sections = document.querySelectorAll('.section');
            const sectionList = document.getElementById('section-list');
            
            toggleSidebar.addEventListener('click', () => {{
                sidebar.classList.toggle('active');
            }});
            
            sections.forEach((section, index) => {{
                const title = section.querySelector('.section-title');
                if (title) {{
                    const listItem = document.createElement('li');
                    const link = document.createElement('a');
                    link.href = `#${{section.id}}`;
                    link.className = 'nav-link';
                    link.textContent = title.textContent;
                    listItem.appendChild(link);
                    sectionList.appendChild(listItem);
                    
                    link.addEventListener('click', (e) => {{
                        e.preventDefault();
                        section.scrollIntoView({{behavior: 'smooth'}});
                        if (window.innerWidth <= 768) {{
                            sidebar.classList.remove('active');
                        }}
                    }});
                }}
            }});
            
            const observerOptions = {{
                root: null,
                rootMargin: '0px',
                threshold: 0.5
            }};
            
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        const id = entry.target.id;
                        document.querySelectorAll('.nav-link').forEach(navLink => {{
                            navLink.classList.remove('active');
                            if (navLink.getAttribute('href') === `#${{id}}`) {{
                                navLink.classList.add('active');
                            }}
                        }});
                    }}
                }});
            }}, observerOptions);
            
            sections.forEach(section => {{
                observer.observe(section);
            }});
        }});
    </script>
</body>
</html>
'''
    return html
import json
from html import escape

def json_to_html(data, level=1):
    html = ""
    if isinstance(data, dict):
        html += f"<section>\n"
        for key, value in data.items():
            if key == "title":
                html += f'<div class="header" level="{level}">{escape(value)}</div>\n'
            elif key == "text":
                if value:
                    html += f"<p>{escape(value)}</p>\n"
            elif key == "content":
                html += json_to_html(value, level + 1)
            elif key == "document":
                html += json_to_html(value, level)
            else:
                html += f"<p><strong>{escape(key)}:</strong> {escape(str(value))}</p>\n"
        html += f"</section>\n"
    elif isinstance(data, list):
        for item in data:
            html += json_to_html(item, level)
    return html

def convert_json_to_html(json_data):
    data = json.loads(json_data)
    html = "<!DOCTYPE html>\n<html>\n<head>\n<style>\n"
    html += "section { margin-left: 20px; }\n"
    html += ".header { font-weight: bold; margin-top: 10px; margin-bottom: 5px; }\n"
    html += "</style>\n</head>\n<body>\n"
    html += json_to_html(data)
    html += "</body>\n</html>"
    return html

# Example usage
json_data = '''
{
    "accession_number": "000143774924010422",
    "cik": "1083522",
    "document": [
        {
            "text": "",
            "content": [
                {
                    "title": "PART I",
                    "text": "",
                    "content": [
                        {
                            "text": "",
                            "content": [
                                {
                                    "title": "Overview",
                                    "text": "This is an overview of Part I.",
                                    "content": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
'''

html_output = convert_json_to_html(json_data)
print(html_output)
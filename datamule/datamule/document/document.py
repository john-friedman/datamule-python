import json
import csv
import re
from doc2dict import xml2dict, txt2dict, dict2dict
from doc2dict.mapping import flatten_hierarchy
from doc2dict import html2dict, visualize_dict, get_title, unnest_dict, pdf2dict
from ..mapping_dicts.txt_mapping_dicts import dict_10k, dict_10q, dict_8k, dict_13d, dict_13g
from ..mapping_dicts.xml_mapping_dicts import dict_345
from ..mapping_dicts.html_mapping_dicts import *
from selectolax.parser import HTMLParser
from .processing import process_tabular_data
from pathlib import Path
import webbrowser

class Document:
    def __init__(self, type, content, extension,accession,filing_date,path=None):
        
        self.type = type
        extension = extension.lower()
        self.accession = accession
        self.filing_date = filing_date
        self.content = content

        if path is not None:
            self.path = path

        self.extension = extension
        # this will be filled by parsed
        self.data = None

    #_load_text_content
    def _preprocess_txt_content(self):
            return self.content.translate(str.maketrans({
                '\xa0': ' ', '\u2003': ' ',
                '\u2018': "'", '\u2019': "'",
                '\u201c': '"', '\u201d': '"'
            }))

    # will deprecate this when we add html2dict
    def _preprocess_html_content(self):
        parser = HTMLParser(self.content,detect_encoding=True,decode_errors='ignore')
    
        # Remove hidden elements first
        hidden_nodes = parser.css('[style*="display: none"], [style*="display:none"], .hidden, .hide, .d-none')
        for node in hidden_nodes:
            node.decompose()
        
        blocks = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article', 'section', 'li', 'td'}
        lines = []
        current_line = []
        
        def flush_line():
            if current_line:
                # Don't add spaces between adjacent spans
                lines.append(''.join(current_line))
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
                        # Only add space if nodes aren't directly adjacent
                        if current_line and not current_line[-1].endswith(' '):
                            if node.prev and node.prev.text_content:
                                if node.parent != node.prev.parent or node.prev.next != node:
                                    current_line.append(' ')
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

    def contains_string(self, pattern):
        """Works for select files"""
        if self.extension in ['.htm', '.html', '.txt','.xml']:
            return bool(re.search(pattern, self.content))
        return False

    # Note: this method will be heavily modified in the future
    def parse(self):
        # check if we have already parsed the content
        if self.data:
            return self.data
        
        mapping_dict = None
        
        if self.extension == '.txt':
            content = self._preprocess_txt_content()
            if self.type == '10-Q':
                mapping_dict = dict_10q
            elif self.type == '10-K':
                mapping_dict = dict_10k
            elif self.type == '8-K':
                mapping_dict = dict_8k
            elif self.type == 'SC 13D':
                mapping_dict = dict_13d
            elif self.type == 'SC 13G':
                mapping_dict = dict_13g
            
            self.data = {}
            self.data['document'] = dict2dict(txt2dict(content=content, mapping_dict=mapping_dict))
        elif self.extension in ['.htm', '.html']:
            
            if self.type == '1-K':
                mapping_dict = dict_1kpartii_html
            elif self.type == '1-SA':
                mapping_dict = dict_1sa_html
            elif self.type == '1-U':
                mapping_dict = dict_1u_html
            elif self.type == '10-12B':
                mapping_dict = dict_1012b_html
            elif self.type == '10-D':
                mapping_dict = dict_10d_html
            elif self.type == '10-K':
                mapping_dict = dict_10k_html
            elif self.type == '10-Q':
                mapping_dict = dict_10q_html
            elif self.type == '20-F':
                mapping_dict = dict_20f_html
            elif self.type == '8-A12B':
                mapping_dict = dict_8a12b_html
            elif self.type == '8-A12G':
                mapping_dict = dict_8a12g_html
            elif self.type == '8-K':
                mapping_dict = dict_8k_html
            elif self.type == '8-K12B':
                mapping_dict = dict_8k12b_html
            elif self.type == '8-K12G3':
                mapping_dict = dict_8k12g3_html
            elif self.type == '8-K15D5':
                mapping_dict = dict_8k15d5_html
            elif self.type == 'ABS-15G':
                mapping_dict = dict_abs15g_html
            elif self.type == 'ABS-EE':
                mapping_dict = dict_absee_html
            elif self.type == 'APP NTC':
                dict_appntc_html
            elif self.type == 'CB':
                mapping_dict = dict_cb_html
            elif self.type == 'SD':
                mapping_dict = dict_sd_html
            elif self.type in ['NT 10-K', 'NT 10-Q','NT 20-F']:
                mapping_dict = dict_nt10k_html
            
            dct = html2dict(content=self.content, mapping_dict=mapping_dict)
            self.data = dct
        elif self.extension == '.xml':
            if self.type in ['3', '4', '5', '3/A', '4/A', '5/A']:
                mapping_dict = dict_345
            
            self.data = xml2dict(content=self.content, mapping_dict=mapping_dict)
        elif self.extension == '.pdf':
            self.data = pdf2dict(content=self.content, mapping_dict=mapping_dict)
        else:
            pass
    
    def write_json(self, output_filename=None):
        if not self.data:
            self.parse()
            
        with open(output_filename, 'w',encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)

    def tables(self):
        if self.type == 'submission_metadata':
            return process_tabular_data(self)
        elif self.extension != '.xml':
            return []
        else:
            self.parse()
            return process_tabular_data(self)


    def write_csv(self, output_folder):
        output_folder = Path(output_folder)
        output_folder.mkdir(exist_ok=True)
            
        tables = self.tables()

        if not tables:
            return
        
        for table in tables:
            fieldnames = table.columns
            output_filename = output_folder / f"{table.type}.csv"

            # Check if the file already exists
            if output_filename.exists():
        
                with open(output_filename, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile,fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                    writer.writerows(table.data)
            else:
                with open(output_filename, 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                    writer.writeheader()
                    writer.writerows(table.data)

        
    def _document_to_section_text(self, document_data, parent_key=''):
        items = []
        
        if isinstance(document_data, dict):
            for key, value in document_data.items():
                # Build the section name
                section = f"{parent_key}_{key}" if parent_key else key
                
                # If the value is a dict, recurse
                if isinstance(value, dict):
                    items.extend(self._document_to_section_text(value, section))
                # If it's a list, handle each item
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            items.extend(self._document_to_section_text(item, f"{section}_{i+1}"))
                        else:
                            items.append({
                                'section': f"{section}_{i+1}",
                                'text': str(item)
                            })
                # Base case - add the item
                else:
                    items.append({
                        'section': section,
                        'text': str(value)
                    })
        
        return items
    
    def visualize(self):
        if not self.data:
            self.parse()

        if not self.data:
            if self.extension in ['.jpg', '.png', '.pdf']:
                webbrowser.open('file://' + str(self.path))
            else:
                pass
        else:
            visualize_dict(self.data)

    def get_section(self, title, format='dict'):
        if not self.data:
            self.parse()

        result = get_title(self.data,title)

        if format == 'text':
            result = [item[1] for item in result]
            result = [unnest_dict(item) for item in result]

        return result

   
   # TODO CHANGE THIS
    def __iter__(self):
        self.parse()

        # Let's remove XML iterable for now

        # Handle text-based documents
        if self.extension in ['.txt', '.htm', '.html']:
            document_data = self.data
            if not document_data:
                return iter([])
                
            # Find highest hierarchy level from mapping dict
            highest_hierarchy = float('inf')
            section_type = None
            
            if self.type in ['10-K', '10-Q']:
                mapping_dict = dict_10k if self.type == '10-K' else dict_10q
            elif self.type == '8-K':
                mapping_dict = dict_8k
            elif self.type == 'SC 13D':
                mapping_dict = dict_13d
            elif self.type == 'SC 13G':
                mapping_dict = dict_13g
            else:
                return iter([])
                
            # Find section type with highest hierarchy number
            highest_hierarchy = -1  # Start at -1 to find highest
            for mapping in mapping_dict['rules']['mappings']:
                if mapping.get('hierarchy') is not None:
                    if mapping['hierarchy'] > highest_hierarchy:
                        highest_hierarchy = mapping['hierarchy']
                        section_type = mapping['name']
                        
            if not section_type:
                return iter([])
                
            # Extract sections of the identified type
            def find_sections(data, target_type):
                sections = []
                if isinstance(data, dict):
                    if data.get('type') == target_type:
                        sections.append({
                            'item': data.get('text', ''),
                            'text': flatten_hierarchy(data.get('content', []))
                        })
                    for value in data.values():
                        if isinstance(value, (dict, list)):
                            sections.extend(find_sections(value, target_type))
                elif isinstance(data, list):
                    for item in data:
                        sections.extend(find_sections(item, target_type))
                return sections
                
            return iter(find_sections(document_data, section_type))
            
        return iter([])
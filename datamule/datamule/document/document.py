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

from pathlib import Path
import webbrowser
from secsgml.utils import bytes_to_str
import tempfile

from .tables.tables import Tables

from ..regex import *

class Document:
    def __init__(self, type, content, extension,accession,filing_date,path=None):
        
        self.type = type
        extension = extension.lower()
        self.accession = accession
        self.filing_date = filing_date

        if self.type == 'submission_metadata':
            # this converts to lower
            self.content = bytes_to_str(content)
        else:
            self.content = content

        if path is not None:
            self.path = path

        self.extension = extension
        # this will be filled by parsed
        self._data = None
        self._tables = None
        self._text = None



    #_load_text_content
    def _preprocess_txt_content(self):
            self._text = self.content.decode().translate(str.maketrans({
                '\xa0': ' ', '\u2003': ' ',
                '\u2018': "'", '\u2019': "'",
                '\u201c': '"', '\u201d': '"'
            }))

    # needs work
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
        
        self._text = text.translate(str.maketrans({
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
        if self._data:
            return
        
        mapping_dict = None
        
        if self.extension == '.txt':
            content = self.text
            if self.type in ['10-Q', '10-Q/A']:
                mapping_dict = dict_10q
            elif self.type in ['10-K','10-K/A']:
                mapping_dict = dict_10k
            elif self.type in ['8-K', '8-K/A']:
                mapping_dict = dict_8k
            elif self.type in ['SC 13D', 'SC 13D/A']:
                mapping_dict = dict_13d
            elif self.type in ['SC 13G', 'SC 13G/A']:
                mapping_dict = dict_13g
            
            self._data = {}
            self._data['document'] = dict2dict(txt2dict(content=content, mapping_dict=mapping_dict))
        elif self.extension in ['.htm', '.html']:
            
            if self.type in ['1-K', '1-K/A']:
                mapping_dict = dict_1kpartii_html
            elif self.type in ['1-SA', '1-SA/A']:
                mapping_dict = dict_1sa_html
            elif self.type in ['1-U', '1-U/A']:
                mapping_dict = dict_1u_html
            elif self.type in ['10-12B', '10-12B/A']:
                mapping_dict = dict_1012b_html
            elif self.type in ['10-D', '10-D/A']:
                mapping_dict = dict_10d_html
            elif self.type in ['10-K', '10-K/A']:
                mapping_dict = dict_10k_html
            elif self.type in ['10-Q', '10-Q/A']:
                mapping_dict = dict_10q_html
            elif self.type in ['20-F', '20-F/A']:
                mapping_dict = dict_20f_html
            elif self.type in ['8-A12B', '8-A12B/A']:
                mapping_dict = dict_8a12b_html
            elif self.type in ['8-A12G', '8-A12G/A']:
                mapping_dict = dict_8a12g_html
            elif self.type in ['8-K', '8-K/A']:
                mapping_dict = dict_8k_html
            elif self.type in ['8-K12B', '8-K12B/A']:
                mapping_dict = dict_8k12b_html
            elif self.type in ['8-K12G3', '8-K12G3/A']:
                mapping_dict = dict_8k12g3_html
            elif self.type in ['8-K15D5', '8-K15D5/A']:
                mapping_dict = dict_8k15d5_html
            elif self.type in ['ABS-15G', 'ABS-15G/A']:
                mapping_dict = dict_abs15g_html
            elif self.type in ['ABS-EE', 'ABS-EE/A']:
                mapping_dict = dict_absee_html
            elif self.type in ['APP NTC', 'APP NTC/A']:
                mapping_dict = dict_appntc_html
            elif self.type in ['CB', 'CB/A']:
                mapping_dict = dict_cb_html
            elif self.type in ['DSTRBRPT', 'DSTRBRPT/A']:
                mapping_dict = dict_dstrbrpt_html
            elif self.type in ['N-18F1', 'N-18F1/A']:
                mapping_dict = dict_n18f1_html
            elif self.type in ['N-CSRS', 'N-CSRS/A']:
                mapping_dict = dict_ncsrs_html
            elif self.type in ['NT-10K', 'NT-10K/A']:
                mapping_dict = dict_nt10k_html
            elif self.type in ['NT-10Q', 'NT-10Q/A']:
                mapping_dict = dict_nt10q_html
            elif self.type in ['NT 20-F', 'NT 20-F/A']:
                mapping_dict = dict_nt20f_html
            elif self.type in ['NT-NCEN', 'NT-NCEN/A']:
                mapping_dict = dict_ntncen_html
            elif self.type in ['NT-NCSR', 'NT-NCSR/A']:
                mapping_dict = dict_ntncsr_html
            elif self.type in ['NTFNCEN', 'NTFNCEN/A']:
                mapping_dict = dict_ntfcen_html
            elif self.type in ['NTFNCSR', 'NTFNCSR/A']:
                mapping_dict = dict_ntfncsr_html
            elif self.type in ['EX-99.CERT', 'EX-99.CERT/A']:
                mapping_dict = dict_ex99cert_html
            elif self.type in ['SC 13E3', 'SC 13E3/A']:
                mapping_dict = dict_sc13e3_html
            elif self.type in ['SC 14D9', 'SC 14D9/A']:
                mapping_dict = dict_sc14d9_html
            elif self.type in ['SP 15D2', 'SP 15D2/A']:
                mapping_dict = dict_sp15d2_html
            elif self.type in ['SD', 'SD/A']:
                mapping_dict = dict_sd_html
            elif self.type in ['S-1', 'S-1/A']:
                mapping_dict = dict_s1_html
            elif self.type in ['T-3', 'T-3/A']:
                mapping_dict = dict_t3_html
            elif self.type in ['NT 10-K', 'NT 10-K/A', 'NT 10-Q', 'NT 10-Q/A', 'NT 20-F', 'NT 20-F/A']:
                mapping_dict = dict_nt10k_html
            
            dct = html2dict(content=self.content, mapping_dict=mapping_dict)
            self._data = dct
        elif self.extension == '.xml':
            if self.type in ['3', '4', '5', '3/A', '4/A', '5/A']:
                mapping_dict = dict_345
            
            self._data = xml2dict(content=self.content, mapping_dict=mapping_dict)
        elif self.extension == '.pdf':
            self._data = pdf2dict(content=self.content, mapping_dict=mapping_dict)
        else:
            pass

    @property
    def data(self):
        if self._data is None:
            self.parse()
        return self._data
    
    @property
    def text(self):
        if self._text is None:
            if self.extension in ['.htm','.html']:
                self._preprocess_html_content()
            elif self.extension == '.txt':
                self._preprocess_txt_content()
        return self._text
    
    def write_json(self, output_filename=None):
        if not self.data:
            self.parse()
            
        with open(output_filename, 'w',encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)

    def parse_tables(self,must_exist_in_mapping=True):
        if self.extension != '.xml':
            self._tables = []
        else:
            # Use the property to trigger parsing if needed
            data = self.data
            tables = Tables(document_type = self.type, accession=self.accession, data=data,must_exist_in_mapping=must_exist_in_mapping)
            self._tables = tables.tables

    @property
    def tables(self):
        if self._tables is None:
            self.parse_tables()
        return self._tables


    def write_csv(self, output_folder):
        output_folder = Path(output_folder)
        output_folder.mkdir(exist_ok=True)
            
        tables = self.tables

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
            pass
        else:
            visualize_dict(self.data)

    # alpha feature
    def open(self):
        """Open the document. Experimental. Creates copy in temp, rather than use tar path for now."""
        if self.extension in ['.htm', '.html','.txt','.jpg','.png', '.pdf']:
            # Create a temporary file with the content and open it

            with tempfile.NamedTemporaryFile(mode='wb', suffix=self.extension, delete=False) as f:
                f.write(self.content)
                temp_path = f.name
            webbrowser.open('file://' + temp_path)
        else:
            print(f"Cannot open files with extension {self.extension}")

    def get_section(self, title=None, title_regex=None,title_class=None, format='dict'):
        if not self.data:
            self.parse()

        result = get_title(self.data,title=title,title_regex=title_regex,title_class=title_class)

        if format == 'text':
            result = [item[1] for item in result]
            result = [unnest_dict(item) for item in result]

        return result

   
   # TODO CHANGE THIS
    def __iter__(self):
        # Use the property to trigger parsing if needed
        document_data = self.data

        # Let's remove XML iterable for now

        # Handle text-based documents
        if self.extension in ['.txt', '.htm', '.html']:
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
import json
import csv
import re
from doc2dict import xml2dict, txt2dict, dict2dict
from doc2dict.mapping import flatten_hierarchy
from doc2dict import html2dict, visualize_dict, get_title, unnest_dict, pdf2dict, flatten_dict
from ..mapping_dicts.txt_mapping_dicts import dict_10k, dict_10q, dict_8k, dict_13d, dict_13g
from ..mapping_dicts.xml_mapping_dicts import dict_345
from ..mapping_dicts.html_mapping_dicts import *
from selectolax.parser import HTMLParser

from pathlib import Path
import webbrowser
from secsgml.utils import bytes_to_str
import tempfile
from .tables.tables import Tables

from ..tags.utils import get_cusip_using_regex, get_isin_using_regex, get_figi_using_regex,get_all_tickers, get_full_names,get_full_names_dictionary_lookup, analyze_lm_sentiment_fragment

class DataWithTags(dict):
    def __init__(self, data, document):
        super().__init__(data)
        self._document = document
        self._tags = None
    
    @property
    def tags(self):
        if self._tags is None:
            self._tags = Tags(self._document, mode='data')  # New fragment-based behavior
        return self._tags
    
    @property
    def similarity(self):
        if not hasattr(self, '_similarity'):
            self._similarity = Similarity(self._document, mode='data')
        return self._similarity
    
class TextWithTags(str):
    def __new__(cls, content, document):
        instance = str.__new__(cls, content)
        instance._document = document
        instance._tags = None
        return instance
    
    @property
    def tags(self):
        if self._tags is None:
            self._tags = Tags(self._document, mode='text')  # Original behavior
        return self._tags
    
    @property
    def similarity(self):
        if not hasattr(self, '_similarity'):
            self._similarity = Similarity(self._document, mode='text')
        return self._similarity
        

class Tickers:
    def __init__(self, document):
        self.document = document
        self._tickers_data = None
    
    def _get_tickers_data(self):
        """Get all tickers data once and cache it"""
        if self._tickers_data is None:
           self._tickers_data = get_all_tickers(self.document.text)
        return self._tickers_data
    
    def __getattr__(self, exchange_name):
        data = self._get_tickers_data()
        
        if exchange_name in data:
            return data[exchange_name]
        
        return []
    
    def __bool__(self):
        """Return True if any tickers were found"""
        data = self._get_tickers_data()
        return bool(data.get('all', []))
    
    def __repr__(self):
        """Show the full ticker data when printed or accessed directly"""
        data = self._get_tickers_data()
        return str(data)
    
    def __str__(self):
        """Show the full ticker data when printed"""
        data = self._get_tickers_data()
        return str(data)
    
class TextAnalysisBase:
    def __init__(self, document, mode='text'):
        from ..tags.config import _active_dictionaries,_loaded_dictionaries
        self.document = document
        self.mode = mode  # 'text' or 'data'
        self.dictionaries = {}
        self.processors = {}
        self._text_sources = None
        
        # Load global dictionaries with their data and processors
        active_dicts = _active_dictionaries
        for dict_name in active_dicts:
            dict_info = _loaded_dictionaries[dict_name]
            self.dictionaries[dict_name] = dict_info['data']
            if dict_info['processor'] is not None:
                self.processors[dict_name] = dict_info['processor']
    
    def _get_text_sources(self):
        """Get text sources based on mode - either single text or multiple fragments"""
        if self._text_sources is None:
            if self.mode == 'text':
                # Original behavior - single text source
                self._text_sources = [{'id': None, 'text': str(self.document.text)}]
            else:  # mode == 'data'
                # New behavior - multiple text fragments
                self._text_sources = []
                self._extract_text_fragments(self.document.data, '')
        return self._text_sources
    
    def _extract_text_fragments(self, data, parent_id=''):
        """Extract all text fragments with their document IDs from parsed data"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ["text", "title"] and isinstance(value, str):
                    # Use the current dictionary's parent key as the fragment ID
                    self._text_sources.append({
                        'id': parent_id,
                        'text': value
                    })
                elif isinstance(value, (dict, list)):
                    # Pass the current key as the parent_id for the next level
                    self._extract_text_fragments(value, key)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    self._extract_text_fragments(item, parent_id)
    
    def _format_results(self, results, fragment_id):
        """Format results based on mode"""
        if self.mode == 'text':
            # Original format: (match, start, end)
            return results
        else:
            # New format: (match, fragment_id, start, end)
            return [(match, fragment_id, start, end) for match, start, end in results]

class Tags(TextAnalysisBase):
    def __init__(self, document, mode='text'):
        super().__init__(document, mode)
        self._tickers = None
    
    @property
    def cusips(self):
        if not hasattr(self, '_cusips'):
            self._cusips = []
            sources = self._get_text_sources()
            
            for source in sources:
                if 'sc13dg_cusips' in self.dictionaries:
                    keywords = self.dictionaries['sc13dg_cusips']
                    results = get_cusip_using_regex(source['text'], keywords)
                elif "13fhr_information_table_cusips" in self.dictionaries:
                    keywords = self.dictionaries['13fhr_information_table_cusips']
                    results = get_cusip_using_regex(source['text'], keywords)
                else:
                    results = get_cusip_using_regex(source['text'])
                
                # Format results based on mode
                formatted_results = self._format_results(results, source['id'])
                self._cusips.extend(formatted_results)
                    
        return self._cusips
    
    @property
    def isins(self):
        if not hasattr(self, '_isins'):
            self._isins = []
            sources = self._get_text_sources()
            
            for source in sources:
                if 'npx_isins' in self.dictionaries:
                    keywords = self.dictionaries['npx_isins']
                    results = get_isin_using_regex(source['text'], keywords)
                else:
                    results = get_isin_using_regex(source['text'])
                
                formatted_results = self._format_results(results, source['id'])
                self._isins.extend(formatted_results)
                    
        return self._isins

    @property
    def figis(self):
        if not hasattr(self, '_figis'):
            self._figis = []
            sources = self._get_text_sources()
            
            for source in sources:
                if 'npx_figis' in self.dictionaries:
                    keywords = self.dictionaries['npx_figis']
                    results = get_figi_using_regex(source['text'], keywords)
                else:
                    results = get_figi_using_regex(source['text'])
                
                formatted_results = self._format_results(results, source['id'])
                self._figis.extend(formatted_results)
                    
        return self._figis
    
    @property
    def tickers(self):
        # Tickers work differently - they need the full document context
        # Keep original behavior for now
        if self._tickers is None:
            self._tickers = Tickers(self.document)
        return self._tickers
    
    @property
    def persons(self):
        if not hasattr(self, '_persons'):
            self._persons = []
            sources = self._get_text_sources()
            for source in sources:
                if '8k_2024_persons' in self.processors:
                    results = get_full_names_dictionary_lookup(source['text'], self.processors['8k_2024_persons'])
                elif 'ssa_baby_first_names' in self.dictionaries:
                    results = get_full_names(source['text'], self.dictionaries['ssa_baby_first_names'])
                else:
                    results = get_full_names(source['text'])
                
                formatted_results = self._format_results(results, source['id'])
                self._persons.extend(formatted_results)
                    
        return self._persons

class Similarity(TextAnalysisBase):
    @property
    def loughran_mcdonald(self):
        if not hasattr(self, '_loughran_mcdonald'):
            self._loughran_mcdonald = []
            sources = self._get_text_sources()
            
            if 'loughran_mcdonald' in self.processors:
                lm_processors = self.processors['loughran_mcdonald']
                
                for source in sources:
                    results = analyze_lm_sentiment_fragment(source['text'], lm_processors)
                    
                    if self.mode == 'text':
                        # Single result for whole document
                        self._loughran_mcdonald = results
                        break
                    else:
                        # Per-fragment results with fragment_id
                        fragment_result = {
                            'fragment_id': source['id'],
                            **results
                        }
                        self._loughran_mcdonald.append(fragment_result)
            else:
                # No processors available
                self._loughran_mcdonald = [] if self.mode == 'data' else {}
                    
        return self._loughran_mcdonald


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
        self._markdown = None

        # booleans
        self._data_bool = self.extension in ('.htm', '.html','.txt')
        self._text_bool = self._data_bool
        self._markdown_bool = self._data_bool
        self._visualize_bool = self._data_bool
        self._tables_bool = self.extension in ('.xml')
        


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

        if self._data is None:
            self._data = {}
        
        if not isinstance(self._data, DataWithTags):
            self._data = DataWithTags(self._data, self)
            
        return self._data
    
    @property
    def text(self):
        if self._text_bool:
            if self._text is None:
                text = flatten_dict(self.data,'text')
                self._text = TextWithTags(text, self)
        return self._text
    
    @property
    def markdown(self):
        if self._markdown_bool:
            if self._markdown is None:
                self._markdown = flatten_dict(self.data,'markdown')

        return self._markdown

    
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

    def reset_nlp(self):
        """Reset all NLP analysis by creating fresh wrapper objects"""
        # Reset data wrapper
        if hasattr(self, '_data') and self._data is not None:
            raw_data = dict(self._data)  # Extract the underlying dict
            self._data = DataWithTags(raw_data, self)
        
        # Reset text wrapper
        if hasattr(self, '_text') and self._text is not None:
            raw_text = str(self._text)  # Extract the underlying string
            self._text = TextWithTags(raw_text, self)
        
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
# sgml_parser.pyx
import os
import json
from io import BytesIO, StringIO
import uu
from cpython.dict cimport PyDict_GetItem, PyDict_SetItem
from libc.string cimport strlen, strchr

cdef class CPythonSGMLParser:
    cdef public buffer_size
    cdef dict _tag_cache
    
    def __init__(self, buffer_size=1024 * 1024):
        self.buffer_size = buffer_size
        self._tag_cache = {}

    cdef _extract_tag_content(self, line):
        if not (line.startswith('<') and '>' in line):
            return None
            
        try:
            tag_end = line.index('>')
            tag = line[1:tag_end]
            
            if tag.startswith('/'):
                return None
                
            if tag not in self._tag_cache:
                self._tag_cache[tag] = tag
            
            content = line[tag_end + 1:].strip()
            return (self._tag_cache[tag], content)
        except:
            return None

    cdef _write_document_content(self, text_buffer, current_document, output_dir):
        if not text_buffer:
            return

        content = ''.join(text_buffer)
        
        if 'FILENAME' in current_document:
            output_path = os.path.join(output_dir, current_document['FILENAME'])
        else:
            output_path = os.path.join(output_dir, f"{current_document.get('SEQUENCE', 'unknown')}.txt")
        
        first_line = content.partition('\n')[0].strip()
        if first_line.startswith('begin '):
            with BytesIO(content.encode()) as input_file:
                uu.decode(input_file, output_path, quiet=True)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

    cpdef parse_file(self, filepath, output_dir):
        cdef:
            dict submission_data = {}
            dict current_document = {}
            list text_buffer = []
            
        os.makedirs(output_dir, exist_ok=True)
        
        metadata_buffer = StringIO()
        metadata_buffer.write('{"submission": {}, "documents": [\n')
        
        state = {
            'in_document': False,
            'in_text': False,
            'in_submission': True,
            'first_document': True
        }
        
        with open(filepath, 'r', buffering=self.buffer_size, encoding='utf-8') as file:
            for line in file:
                stripped = line.strip()
                
                if stripped == '<DOCUMENT>':
                    state['in_document'] = True
                    state['in_submission'] = False
                    if not state['first_document']:
                        metadata_buffer.write(',\n')
                    current_document = {}
                    
                elif stripped == '</DOCUMENT>':
                    metadata_buffer.write(json.dumps(current_document))
                    state['first_document'] = False
                    self._write_document_content(text_buffer, current_document, output_dir)
                    text_buffer = []
                    state['in_document'] = False
                    current_document = {}
                    
                elif stripped == '<TEXT>':
                    state['in_text'] = True
                    text_buffer = []
                    
                elif stripped == '</TEXT>':
                    state['in_text'] = False
                    
                elif state['in_text']:
                    if stripped not in ['<PDF>', '</PDF>']:
                        text_buffer.append(line)
                        
                else:
                    tag_content = self._extract_tag_content(stripped)
                    if tag_content:
                        key, value = tag_content
                        if state['in_submission']:
                            submission_data[key] = value
                        elif state['in_document']:
                            current_document[key] = value
        
        metadata_buffer.write('\n]}')
        metadata_str = metadata_buffer.getvalue()
        metadata_buffer.close()
        
        metadata_path = os.path.join(output_dir, 'metadata.json')
        metadata = json.loads(metadata_str)
        metadata['submission'] = submission_data
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)

def parse_sgml_submission(filepath, output_dir=None):
    if output_dir is None:
        output_dir = os.path.splitext(filepath)[0] + '_output'
        
    parser = CPythonSGMLParser()
    parser.parse_file(filepath, output_dir)
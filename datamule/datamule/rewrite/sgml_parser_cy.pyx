# sgml_parser.pyx
import os
import json
import uu
from io import BytesIO
from cpython cimport PyBytes_FromString
from libc.string cimport strlen, strncmp

cdef class CySGMLParser:
    cdef public str output_dir
    
    cdef bint _is_tag(self, const char* line, size_t length):
        return line[0] == b'<' and line[length-1] == b'>'
    
    cdef tuple _extract_tag_content(self, str line):
        cdef:
            size_t tag_end = line.index('>')
            str tag = line[1:tag_end]
            str content
            
        if tag.startswith('/'):
            return None
            
        content = line[tag_end + 1:].strip()
        return (tag, content)

    cdef void _write_document(self, str content, dict document_info):
        cdef str output_path, first_line
        
        if not content:
            return

        output_path = os.path.join(self.output_dir, document_info.get('FILENAME', f"{document_info.get('SEQUENCE', 'unknown')}.txt"))
        first_line = content.partition('\n')[0].strip()
        
        if first_line.startswith('begin '):
            with BytesIO(content.encode()) as input_file:
                uu.decode(input_file, output_path, quiet=True)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

    cpdef parse_file(self, str filepath):
        cdef:
            dict submission_data = {}
            list documents = []
            dict current_document = {}
            list text_buffer = []
            bint in_document = False
            bint in_text = False
            bint in_submission = True
            str line, stripped
            tuple tag_content
        
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                stripped = line.strip()
                
                if stripped == '<DOCUMENT>':
                    in_document = True
                    in_submission = False
                    current_document = {}
                    
                elif stripped == '</DOCUMENT>':
                    documents.append(current_document)
                    self._write_document(''.join(text_buffer), current_document)
                    text_buffer = []
                    in_document = False
                    
                elif stripped == '<TEXT>':
                    in_text = True
                    text_buffer = []
                    
                elif stripped == '</TEXT>':
                    in_text = False
                    
                elif in_text:
                    if stripped not in ['<PDF>', '</PDF>']:
                        text_buffer.append(line)
                        
                else:
                    tag_content = self._extract_tag_content(stripped)
                    if tag_content:
                        key, value = tag_content
                        if in_submission:
                            submission_data[key] = value
                        elif in_document:
                            current_document[key] = value
        
        metadata = {
            'submission': submission_data,
            'documents': documents
        }
        
        with open(os.path.join(self.output_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)

def parse_sgml_submission(filepath: str, output_dir: str | None = None) -> None:
    if output_dir is None:
        output_dir = os.path.splitext(filepath)[0] + '_output'
    
    os.makedirs(output_dir, exist_ok=True)
    
    parser = CySGMLParser()
    parser.output_dir = output_dir
    parser.parse_file(filepath)
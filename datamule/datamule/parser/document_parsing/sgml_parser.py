import os
import json
import uu
from io import BytesIO

class SimpleSGMLParser:
    def _extract_tag_content(self, line: str) -> tuple[str, str] | None:
        if not (line.startswith('<') and '>' in line):
            return None
            
        tag_end = line.index('>')
        tag = line[1:tag_end]
        
        if tag.startswith('/'):
            return None
        
        content = line[tag_end + 1:].strip()
        return (tag, content)

    def _write_document(self, content: str, document_info: dict, output_dir: str) -> None:
        if not content:
            return

        output_path = os.path.join(output_dir, document_info.get('FILENAME', f"{document_info.get('SEQUENCE', 'unknown')}.txt"))
        
        first_line = content.partition('\n')[0].strip()
        if first_line.startswith('begin '):
            with BytesIO(content.encode()) as input_file:
                uu.decode(input_file, output_path,quiet=True)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def parse_file(self, filepath: str, output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)
        
        submission_data = {}
        documents = []
        current_document = {}
        text_buffer = []
        
        in_document = False
        in_text = False
        in_submission = True
        
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                stripped = line.strip()
                
                if stripped == '<DOCUMENT>':
                    in_document = True
                    in_submission = False
                    current_document = {}
                    
                elif stripped == '</DOCUMENT>':
                    documents.append(current_document)
                    self._write_document(''.join(text_buffer), current_document, output_dir)
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
        
        with open(os.path.join(output_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)

def parse_sgml_submission(filepath: str, output_dir: str | None = None) -> None:
    if output_dir is None:
        output_dir = os.path.splitext(filepath)[0] + '_output'
        
    parser = SimpleSGMLParser()
    parser.parse_file(filepath, output_dir)
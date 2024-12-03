import shutil
import os
import json
import io
import uu
import mmap

def read_line(line):
    try:
        key = line.split('<')[1].split('>')[0]
        value = ''
        if key.startswith('/'):
            return None
        if line.endswith('>'):
            return {key: {}}
        value = line.split('>', 1)[1].strip()
        return {key: value}
    except:
        raise ValueError(f"Could not parse line: {line}")

def parse_sgml_submission(filepath, output_dir=None, header_only=False):
    if not header_only and output_dir:
        shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir, exist_ok=True)

    metadata = {
        'submission': {},
        'documents': [] if not header_only else None
    }
    
    tag_stack = []
    path_stack = [metadata['submission']]
    current_document = None
    text_content = []
    last_key = None
    in_text = False
    in_header = False
    
    with open(filepath, 'rb') as file:
        with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            # Read first line to determine type
            first_line = mm.readline().decode('utf-8').rstrip('\n')
            is_submission = '<SEC-DOCUMENT>' in first_line
            mm.seek(0)  # Reset to start
            
            while True:
                line = mm.readline()
                if not line:  # EOF
                    break
                    
                try:
                    original_line = line.decode('utf-8').rstrip('\n')
                except UnicodeDecodeError:
                    continue  # Skip lines that can't be decoded
                    
                stripped_line = original_line.strip()
                
                # Handle SEC-HEADER section for submission files
                if is_submission:
                    if stripped_line == '<SEC-HEADER>':
                        in_header = True
                        continue
                    elif stripped_line == '</SEC-HEADER>':
                        in_header = False
                        continue
                    elif in_header:
                        # Parse header content into submission metadata
                        if stripped_line.startswith('<'):
                            parsed = read_line(stripped_line)
                            if parsed:
                                key = list(parsed.keys())[0]
                                metadata['submission'][key] = parsed[key]
                        continue
                
                if stripped_line == '<DOCUMENT>':
                    if header_only:
                        return metadata['submission']
                    current_document = {}
                    metadata['documents'].append(current_document)
                    path_stack = [current_document]
                    tag_stack.append('DOCUMENT')
                    last_key = None
                    
                elif stripped_line == '</DOCUMENT>':
                    if current_document and text_content:
                        if 'FILENAME' in current_document:
                            output_path = os.path.join(output_dir, current_document['FILENAME'])
                            content = '\n'.join(text_content)
                            
                            # For XML files, check and strip XML wrapper tags if present
                            if (current_document['FILENAME'].lower().endswith('.xml') and 
                                content.strip().startswith('<XML>') and content.strip().endswith('</XML>')):
                                content = '\n'.join(content.split('\n')[1:-1])
                                
                            with open(output_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        elif 'SEQUENCE' in current_document:
                            output_path = os.path.join(output_dir, f'{current_document["SEQUENCE"]}.txt')
                            with open(output_path, 'w', encoding='utf-8') as f:
                                f.write('\n'.join(text_content))
                        else:
                            raise ValueError("Document does not have a FILENAME or SEQUENCE")
                                
                    text_content = []
                    current_document = None
                    path_stack = [metadata['submission']]
                    tag_stack.pop()
                    last_key = None
                    
                elif stripped_line == '<TEXT>':
                    in_text = True
                    text_content = []
                    tag_stack.append('TEXT')
                    last_key = None
                    
                elif stripped_line == '</TEXT>':
                    in_text = False
                    tag_stack.pop()
                    
                elif in_text:
                    if stripped_line not in ['<PDF>', '</PDF>']:
                        text_content.append(original_line)
                    
                else:
                    if stripped_line.startswith('<'):
                        parsed = read_line(stripped_line)
                        if parsed is None:
                            if tag_stack:
                                tag_stack.pop()
                                if len(path_stack) > 1:
                                    path_stack.pop()
                                last_key = None
                        else:
                            key = list(parsed.keys())[0]
                            value = parsed[key]
                            
                            if isinstance(value, dict):
                                current_dict = path_stack[-1]
                                current_dict[key] = {}
                                path_stack.append(current_dict[key])
                                tag_stack.append(key)
                                last_key = None
                            else:
                                current_dict = path_stack[-1]
                                current_dict[key] = value
                                last_key = key
                    elif last_key:
                        current_dict = path_stack[-1]
                        current_dict[last_key] += ' ' + stripped_line

    if header_only:
        return metadata['submission']
        
    metadata_path = os.path.join(output_dir, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    
    return metadata
import shutil
import os
import json
import io
import uu

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

def parse_submission_from_feed(filepath, output_dir=None, header_only=False):
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
    
    with open(filepath, 'r') as file:
        for line in file:
            original_line = line.rstrip('\n')
            stripped_line = original_line.strip()
            
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
                    elif 'SEQUENCE' in current_document:
                        output_path = os.path.join(output_dir, f'{current_document["SEQUENCE"]}.txt')
                    else:
                        raise ValueError("Document does not have a FILENAME or SEQUENCE")
                    
                    content = '\n'.join(text_content)
                    first_line = next((line for line in content.split('\n') if line.strip()), '')
                    
                    if first_line.startswith('begin '):
                        input_file = io.BytesIO(content.encode())
                        uu.decode(input_file, output_path, quiet=True)
                    else:
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                            
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
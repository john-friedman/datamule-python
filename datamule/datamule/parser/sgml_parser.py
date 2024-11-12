import shutil
import os
import json
from time import time

def UUdecoder(text):
    # skip first and last line
    text = text.split('\n')[1:-1]
    result = bytearray()
    
    for line in text:
        if not line: 
            continue
            
        length = (ord(line[0]) - 32) & 63
        chars = line[1:]
        
        for i in range(0, len(chars), 4):
            group = chars[i:i+4]
            if len(group) < 4:
                break
                
            n = 0
            for c in group:
                n = n * 64 + ((ord(c) - 32) & 63)
            
            result.append((n >> 16) & 0xFF)
            if length > 1:
                result.append((n >> 8) & 0xFF)
            if length > 2:
                result.append(n & 0xFF)
            
            length -= 3
            if length <= 0:
                break
                
    return bytes(result)

def read_line(line):
    key = line.split('<')[1].split('>')[0]
    value = ''
    if key.startswith('/'):
        return None
    if line.endswith('>'):
        return {key: {}}
    value = line.split('>', 1)[1].strip()
    return {key: value}

# Parses a submission file in SGML format (e.g. nc)
def parse_submission(filepath, output_dir):
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)

    metadata = {
        'submission': {},
        'documents': []
    }
    
    tag_stack = []
    path_stack = [metadata['submission']]
    current_document = None
    text_content = []
    in_text = False
    
    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            
            if line == '<SUBMISSION>':
                tag_stack.append('SUBMISSION')
                
            elif line == '</SUBMISSION>':
                tag_stack.pop()
                
            elif line == '<DOCUMENT>':
                current_document = {}
                metadata['documents'].append(current_document)
                path_stack = [current_document]
                tag_stack.append('DOCUMENT')
                
            elif line == '</DOCUMENT>':
                if current_document and text_content and 'FILENAME' in current_document:
                    output_path = os.path.join(output_dir, current_document['FILENAME'])
                    
                    # Check if content is UUencoded
                    if text_content and text_content[0].startswith('begin 644'):
                        # Join with newlines and decode
                        content = UUdecoder('\n'.join(text_content))
                        # Write binary content
                        with open(output_path, 'wb') as f:
                            f.write(content)
                    else:
                        # Write normal text content
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(text_content))
                            
                text_content = []
                current_document = None
                path_stack = [metadata['submission']]
                tag_stack.pop()
                
            elif line == '<TEXT>':
                in_text = True
                text_content = []
                tag_stack.append('TEXT')
                
            elif line == '</TEXT>':
                in_text = False
                tag_stack.pop()
                
            elif in_text:
                text_content.append(line)
                
            else:
                parsed = read_line(line)
                if parsed is None:  # Closing tag
                    if tag_stack:
                        tag_stack.pop()
                        if len(path_stack) > 1:  # Don't pop the root stack
                            path_stack.pop()
                else:  # Opening tag or value
                    key = list(parsed.keys())[0]
                    value = parsed[key]
                    
                    if isinstance(value, dict):  # Opening tag
                        current_dict = path_stack[-1]
                        current_dict[key] = {}
                        path_stack.append(current_dict[key])
                        tag_stack.append(key)
                    else:  # Value tag
                        current_dict = path_stack[-1]
                        current_dict[key] = value
    
    metadata_path = os.path.join(output_dir, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    
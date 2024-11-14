import shutil
import os
import json

# fix uudecoder
# test for jpg / pdf


class UUEncodeError(Exception):
    pass


def UUdecoder(text):
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
    last_key = None

    in_text = False
    is_uuencoded = False
    
    
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
                last_key = None
                
            elif line == '</DOCUMENT>':
                if current_document and text_content:
                    if 'FILENAME' in current_document:
                        output_path = os.path.join(output_dir, current_document['FILENAME'])
                    elif 'SEQUENCE' in current_document:
                        output_path = os.path.join(output_dir, f'{current_document["SEQUENCE"]}.txt')
                    else:
                        raise ValueError("Document does not have a FILENAME or SEQUENCE")
                    
                    if is_uuencoded:
                        content = UUdecoder('\n'.join(text_content))
                        with open(output_path, 'wb') as f:
                            f.write(content)
                    else:
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(text_content))
                            
                text_content = []
                current_document = None
                path_stack = [metadata['submission']]
                tag_stack.pop()
                last_key = None
                
            elif line == '<TEXT>':
                in_text = True
                text_content = []
                tag_stack.append('TEXT')
                last_key = None
                
            elif line == '</TEXT>':
                in_text = False
                tag_stack.pop()
                
            elif line == '':
                pass
                
            elif in_text:
                # where we target uuencode
                if line:
                    if not text_content:  # First non-empty line
                        if line.startswith('begin 644'):
                            is_uuencoded = True

                    text_content.append(line)
                
            else:
                if line.startswith('<'):
                    parsed = read_line(line)
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
                    current_dict[last_key] += ' ' + line.strip()
    
    metadata_path = os.path.join(output_dir, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
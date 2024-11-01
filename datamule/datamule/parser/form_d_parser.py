from xml.etree import ElementTree as ET

def element_to_dict(elem):
    """Convert an XML element to dict preserving structure."""
    result = {}
    
    # Add attributes directly to result
    if elem.attrib:
        result.update(elem.attrib)
        
    # Add text content if present and no children
    if elem.text and elem.text.strip():
        text = elem.text.strip()
        if not len(elem):  # No children
            return text
        else:
            result['text'] = text
            
    # Process children
    for child in elem:
        child_data = element_to_dict(child)
        child_tag = child.tag.split('}')[-1]  # Remove namespace
        
        if child_tag in result:
            # Convert to list if multiple elements
            if not isinstance(result[child_tag], list):
                result[child_tag] = [result[child_tag]]
            result[child_tag].append(child_data)
        else:
            result[child_tag] = child_data
            
    return result

def parse_form_d(filepath):
    """Parse Form D XML file into metadata and document sections."""
    # Parse XML
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # Remove namespaces for cleaner processing
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}')[-1]
    
    # Convert entire document to dict
    full_dict = element_to_dict(root)
    
    # Separate metadata and document content
    result = {
        'metadata': {},
        'document': {}
    }
    
    # Extract metadata
    metadata_fields = {
        'schemaVersion',
        'submissionType',
        'testOrLive',
        'primaryIssuer'  # Including all issuer information in metadata
    }
    
    for field in metadata_fields:
        if field in full_dict:
            result['metadata'][field] = full_dict[field]
            del full_dict[field]  # Remove from full_dict to avoid duplication
    
    # Everything else goes to document
    result['document'] = full_dict
    
    return result
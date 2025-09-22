import zstandard as zstd
from secsgml.utils import calculate_documents_locations_in_tar
import tarfile
import io
import json

# Note: we don't actually need accession at this level. TODO

def compress_content(content, compression_type, level):
    if compression_type == 'zstd':
        # Create compressor with specified level
        compressor = zstd.ZstdCompressor(level=level)
        
        # Handle string content
        # This should never be called
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
            
        # Compress and return
        return compressor.compress(content_bytes)
    
    # Return uncompressed if not zstd
    return content

def compress_content_list(document_tuple_list, compression_type, level):
    if compression_type is None:
        return document_tuple_list
    
    if level is None:
        level = 3

    # Create new list to avoid modifying original
    compressed_list = []
    for document_tuple in document_tuple_list:
        content = document_tuple[0]  
        accession = document_tuple[1]
        compressed_content = compress_content(content, compression_type, level)
        compressed_list.append((compressed_content, accession))
    
    return compressed_list

def tar_content_list(metadata, document_tuple_list_compressed):
    # Update metadata with compressed sizes
    for i, (content, accession) in enumerate(document_tuple_list_compressed):  
        metadata['documents'][i]['secsgml_size_bytes'] = len(content)
    
    metadata = calculate_documents_locations_in_tar(metadata)

    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w') as tar:  
        # Add metadata first
        metadata_json = json.dumps(metadata).encode('utf-8')
        tarinfo = tarfile.TarInfo(f'metadata.json')
        tarinfo.size = len(metadata_json)
        tar.addfile(tarinfo, io.BytesIO(metadata_json))
        
        # Add each content
        for i, (content, accession) in enumerate(document_tuple_list_compressed): 
            doc = metadata['documents'][i]
            filename = doc.get('filename', doc['sequence'] + '.txt')
            
            tarinfo = tarfile.TarInfo(name=filename)
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content)) 
    
    # Return the tar buffer
    tar_buffer.seek(0)  # Reset buffer position to beginning
    return tar_buffer

def tar_submission(metadata, documents_obj_list, compression_type=None, level=None):
    """Takes a list of documents, compresses them, then tars them."""
    document_tuple_list = [(doc.content, doc.accession) for doc in documents_obj_list]
    document_tuple_list_compressed = compress_content_list(document_tuple_list,  # Fixed: correct parameter name
                                                          compression_type=compression_type, 
                                                          level=level)

    return tar_content_list(metadata, document_tuple_list_compressed)
import zstandard as zstd
import io
import shutil

def create_compressor(level=6):
    return zstd.ZstdCompressor(level=level)

def compress_content(content, compressor, encoding='utf-8'):
    if isinstance(content, str):
        content_bytes = content.encode(encoding)
    else:
        content_bytes = content
    
    compressed = compressor.compress(content_bytes)
    return compressed

def decompress_content(compressed_data):
    dctx = zstd.ZstdDecompressor()
    
    # Handle both single bytes object and list of chunks
    if isinstance(compressed_data, list):
        input_buffer = io.BytesIO(b''.join(compressed_data))
    else:
        input_buffer = io.BytesIO(compressed_data)
    
    decompressed_content = io.BytesIO()
    
    try:
        with dctx.stream_reader(input_buffer) as reader:
            shutil.copyfileobj(reader, decompressed_content)
        
        return decompressed_content.getvalue()
    finally:
        input_buffer.close()
        decompressed_content.close()
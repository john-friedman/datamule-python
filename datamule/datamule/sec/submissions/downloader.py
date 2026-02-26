import os
from .streamer import stream
from tqdm import tqdm 
from ...helper import _process_cik_and_metadata_filters
import tarfile
import io
from secsgml2 import parse_sgml_content_into_memory
from secsgml2.utils import calculate_documents_locations_in_tar


# Moved from secsgml original
def write_submission_to_tar(output_path,metadata,documents):
     # Write tar directly to disk
    with tarfile.open(output_path, 'w') as tar:

        # calculate document locations in tar
        metadata = calculate_documents_locations_in_tar(metadata)
        metadata_json = json.dumps(metadata).encode('utf-8')
        
        # save metadata
        tarinfo = tarfile.TarInfo(name='metadata.json')
        tarinfo.size = len(metadata_json)
        tar.addfile(tarinfo, io.BytesIO(metadata_json))

        for file_num, content in enumerate(documents, 0):
            document_name = metadata['documents'][file_num]['filename'] if metadata['documents'][file_num].get('filename') else metadata['documents'][file_num]['sequence'] + '.txt'
            tarinfo = tarfile.TarInfo(name=f'{document_name}')
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content))

def write_sgml_file_to_tar(output_path, bytes_content=None, input_path=None,filter_document_types=[]):
    # Validate input arguments
    if bytes_content is None and input_path is None:
        raise ValueError("Either bytes_content or input_path must be provided")
    
    if bytes_content is not None and input_path is not None:
        raise ValueError("Cannot provide both bytes_content and input_path - choose one")
    
    # Validate output_path is provided
    if output_path is None:
        raise ValueError("output_path is required")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else 'output', exist_ok=True)
    
    # Get data either from file or direct content
    if input_path is not None:
        if not os.path.exists(input_path):
            raise ValueError("Filepath not found")
        
        with open(input_path, 'rb') as f:
            bytes_content = f.read()
            metadata, documents = parse_sgml_content_into_memory(data=bytes_content,filter_document_types=filter_document_types)
    else:
        # Use content directly
        metadata, documents = parse_sgml_content_into_memory(data=bytes_content, filter_document_types=filter_document_types)
    
    write_submission_to_tar(output_path,metadata,documents)

# end #



def download(cik=None, submission_type=None, filing_date=None, location=None, name=None, 
             requests_per_second=5, output_dir="filings", filtered_accession_numbers=None, 
             quiet=False, keep_document_types=[],
             skip_accession_numbers=[],ticker=None,**kwargs):
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    pbar = tqdm(desc="Writing", unit=" submissions", disable=quiet,position=2)

    # Create a wrapper for the download_callback that includes the output_dir
    async def callback_wrapper(hit, content, cik, accno, url):
        output_path = os.path.join(output_dir, accno.replace('-','') + '.tar')
        write_sgml_file_to_tar(output_path, bytes_content=content, filter_document_types=keep_document_types)
        pbar.update(1)

    cik =  _process_cik_and_metadata_filters(cik, ticker, **kwargs)

    # Call the stream function with our callback
    return stream(
        cik=cik,
        name=name,
        submission_type=submission_type,
        filing_date=filing_date,
        location=location,
        requests_per_second=requests_per_second,
        document_callback=callback_wrapper,
        filtered_accession_numbers=filtered_accession_numbers,
        skip_accession_numbers=skip_accession_numbers,
        quiet=quiet
    )

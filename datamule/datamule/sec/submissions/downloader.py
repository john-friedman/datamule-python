import os
from .streamer import stream
from secsgml import write_sgml_file_to_tar
from tqdm import tqdm

def download(cik=None, submission_type=None, filing_date=None, location=None, name=None, 
             requests_per_second=5, output_dir="filings", filtered_accession_numbers=None, 
             quiet=False, keep_document_types=[],keep_filtered_metadata=False,standardize_metadata=True,
             skip_accession_numbers=[]):
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    pbar = tqdm(desc="Writing", unit=" submissions", disable=quiet,position=2)

    # Create a wrapper for the download_callback that includes the output_dir
    async def callback_wrapper(hit, content, cik, accno, url):
        output_path = os.path.join(output_dir, accno.replace('-','') + '.tar')
        write_sgml_file_to_tar(output_path, bytes_content=content, filter_document_types=keep_document_types,keep_filtered_metadata=keep_filtered_metadata,
                               standardize_metadata=standardize_metadata)
        pbar.update(1)


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
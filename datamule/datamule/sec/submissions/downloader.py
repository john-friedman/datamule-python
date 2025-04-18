import os
import json
from .streamer import stream
import aiofiles
from ...submission import Submission

async def download_callback(hit, content, cik, accno, url, output_dir="filings", keep_document_types=None):
    """Save downloaded SEC submission to disk."""
    try:
        # Create a Submission object directly from the content
        # Note: the content needs to be decoded from bytes to string for the parser
        submission = Submission(sgml_content=content.decode('utf-8', errors='replace'), 
                               keep_document_types=keep_document_types)
        
        # Use the async save method to write the submission to disk
        file_dir = await submission.save_async(output_dir=output_dir)
        
        return file_dir
    except Exception as e:
        print(f"Error processing {accno}: {e}")
        return None

def download(cik=None, submission_type=None, filing_date=None, location=None, name=None, 
             requests_per_second=5, output_dir="filings", accession_numbers=None, 
             quiet=False, keep_document_types=None):
    """
    Download SEC EDGAR filings and extract their documents.
    
    Parameters:
    - cik: CIK number(s) to query for
    - submission_type: Filing type(s) to query for (default: 10-K)
    - filing_date: Date or date range to query for
    - location: Location code to filter by (e.g., 'CA' for California)
    - name: Company name to search for (alternative to providing CIK)
    - requests_per_second: Rate limit for SEC requests
    - output_dir: Directory to save documents
    - accession_numbers: Optional list of accession numbers to filter by
    - quiet: Whether to suppress progress output
    - keep_document_types: Optional list of document types to keep (e.g. ['10-K', 'EX-10.1'])
    
    Returns:
    - List of all document paths processed
    """
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a wrapper for the download_callback that includes the output_dir
    async def callback_wrapper(hit, content, cik, accno, url):
        return await download_callback(hit, content, cik, accno, url, 
                                     output_dir=output_dir,
                                     keep_document_types=keep_document_types)
    
    # Call the stream function with our callback
    return stream(
        cik=cik,
        name=name,
        submission_type=submission_type,
        filing_date=filing_date,
        location=location,
        requests_per_second=requests_per_second,
        document_callback=callback_wrapper,
        accession_numbers=accession_numbers,
        quiet=quiet
    )
import os
import json
from .streamer import stream
from secsgml import parse_sgml_submission_into_memory
import aiofiles

async def download_callback(hit, content, cik, accno, url, output_dir="filings"):
    """Save downloaded SEC submission to disk."""
    try:
        # Parse the SGML content
        metadata, documents = parse_sgml_submission_into_memory(content=content.decode('utf-8', errors='replace'))
        
        # Create folder structure: output_dir/accno
        file_dir = os.path.join(output_dir, str(accno))
        os.makedirs(file_dir, exist_ok=True)
        
        # Save metadata
        metadata_path = os.path.join(file_dir, "metadata.json")
        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(json.dumps(metadata, indent=4))

        # Save all documents
        for idx, _ in enumerate(metadata['documents']):
            try:
                filename = metadata['documents'][idx]['filename']
            except (KeyError, IndexError):
                filename = f"{metadata['documents'][idx].get('sequence', idx)}.txt"

            # Use async file writing
            doc_path = os.path.join(file_dir, filename)
            async with aiofiles.open(doc_path, 'wb') as f:
                await f.write(documents[idx])
        
        return file_dir
    except Exception as e:
        print(f"Error processing {accno}: {e}")
        return None

def download(cik=None, submission_type=None, filing_date=None, location=None, name=None, 
             requests_per_second=5, output_dir="filings", accession_numbers=None, quiet=False):
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
    
    Returns:
    - List of all document paths processed
    
    Examples:
    # Download filings by CIK
    download(cik="1318605", submission_type="10-K")
    
    # Download filings by company name
    download(name="Tesla", submission_type="10-K")
    
    # Download filings with location filter
    download(name="Apple", location="CA", submission_type="10-K")
    """
        
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a wrapper for the download_callback that includes the output_dir
    async def callback_wrapper(hit, content, cik, accno, url):
        return await download_callback(hit, content, cik, accno, url, output_dir=output_dir)
    
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
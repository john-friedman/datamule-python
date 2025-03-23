import zipfile
import os
import json
import csv
import gzip
import asyncio
import aiohttp
import tempfile
from tqdm import tqdm
from datetime import datetime
from ..utils import headers

async def download_sec_file(url, target_path):
    """Download submissions.zip from SEC website with progress bar."""
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"Failed to download: HTTP {response.status}")
            
            file_size = int(response.headers.get('Content-Length', 0))
            
            with tqdm(total=file_size, unit='B', unit_scale=True, desc="Downloading SEC data") as progress_bar:
                with open(target_path, 'wb') as f:
                    chunk_size = 1024 * 1024  # 1MB chunks
                    downloaded = 0
                    
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress_bar.update(len(chunk))
    
    print(f"Download complete: {target_path}")
    return target_path

def extract_metadata(data):
    """Extract and flatten relevant company metadata from SEC submission data."""
    result = {}
    
    # Extract top-level fields, but exclude formerNames as it will be processed separately
    for key in ['cik', 'entityType', 'sic', 'sicDescription', 'ownerOrg', 
              'insiderTransactionForOwnerExists', 'insiderTransactionForIssuerExists',
              'name', 'tickers', 'exchanges', 'ein', 'description', 'category', 'fiscalYearEnd', 'stateOfIncorporation',
              'stateOfIncorporationDescription', 'phone', 'flags']:
        result[key] = data.get(key)
    
    # Extract address fields
    if 'addresses' in data:
        for addr_type in ['mailing', 'business']:
            if addr_type in data['addresses']:
                addr = data['addresses'][addr_type]
                for field in ['street1', 'street2', 'city', 'stateOrCountry', 'zipCode', 'stateOrCountryDescription']:
                    result[f"{addr_type}_{field}"] = addr.get(field)
    
    # Add start_date field (will be populated later)
    result['start_date'] = ''
    
    return result

def extract_earliest_filing_date(data):
    """Extract the earliest filing date from the full JSON data."""
    earliest_date = None
    
    # Try to get dates from the filings.files array first
    if 'filings' in data and 'files' in data['filings'] and isinstance(data['filings']['files'], list):
        for file_info in data['filings']['files']:
            if isinstance(file_info, dict) and 'filingFrom' in file_info:
                file_date = file_info.get('filingFrom', '')
                if file_date and (earliest_date is None or file_date < earliest_date):
                    earliest_date = file_date
    
    # If no date found in files array, check filingDate array in filings.recent
    if earliest_date is None and 'filings' in data and 'recent' in data['filings']:
        if 'filingDate' in data['filings']['recent'] and isinstance(data['filings']['recent']['filingDate'], list):
            filing_dates = data['filings']['recent']['filingDate']
            for filing_date in filing_dates:
                if filing_date and (earliest_date is None or filing_date < earliest_date):
                    earliest_date = filing_date
    
    return earliest_date

def process_former_names(data, cik, current_name):
    """
    Process former names into a list of records.
    Returns former names records and the earliest company date.
    """
    former_names_records = []
    earliest_company_date = None
    
    # Process former names if present
    former_names = data.get('formerNames', [])
    
    # Track the latest end date to use for current name start date
    latest_end_date = None
    
    if former_names and isinstance(former_names, list):
        for former_name in former_names:
            if isinstance(former_name, dict):
                # Extract name, start date, and end date
                name = former_name.get('name', '')
                start_date = former_name.get('from', '')
                end_date = former_name.get('to', '')
                
                # Clean up date formats (remove time component)
                if start_date:
                    start_date = start_date.split('T')[0]
                    # Track earliest company date across all former names
                    if earliest_company_date is None or start_date < earliest_company_date:
                        earliest_company_date = start_date
                        
                if end_date:
                    end_date = end_date.split('T')[0]
                    # Track latest end date
                    if not latest_end_date or end_date > latest_end_date:
                        latest_end_date = end_date
                
                # Create record for former name
                record = {
                    'name': name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'cik': cik
                }
                
                former_names_records.append(record)
    
    # Find the earliest filing date for the company if no date found in former names
    if earliest_company_date is None:
        earliest_company_date = extract_earliest_filing_date(data)
        if earliest_company_date and 'T' in earliest_company_date:
            earliest_company_date = earliest_company_date.split('T')[0]
    
    # For the current name, if we don't have a start date from former names,
    # we'll use the earliest filing date
    if not latest_end_date:
        latest_end_date = earliest_company_date
    
    # Add current name record with start date as latest end date
    current_record = {
        'name': current_name,
        'start_date': latest_end_date if latest_end_date else '',
        'end_date': '',  # Current name has no end date
        'cik': cik
    }
    
    former_names_records.append(current_record)
    
    # Return both the records and the earliest company date (for metadata)
    return former_names_records, earliest_company_date

def write_metadata_to_csv(metadata_list, output_path):
    """Write metadata records to CSV and compress with gzip."""
    if not metadata_list:
        return
    
    # Add .gz extension if not already present
    if not output_path.endswith('.gz'):
        output_path = output_path + '.gz'
    
    # Get all possible field names across all records
    fieldnames = set()
    for metadata in metadata_list:
        fieldnames.update(metadata.keys())
    
    # Make sure 'name', 'cik', and 'start_date' come first
    fieldnames = ['name', 'cik', 'start_date'] + [f for f in sorted(fieldnames) if f not in ['name', 'cik', 'start_date']]
    
    # Write directly to gzipped CSV without using StringIO buffer
    with gzip.open(output_path, 'wt', encoding='utf-8', newline='') as gzfile:
        writer = csv.DictWriter(gzfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metadata_list)
    
    print(f"Wrote {len(metadata_list)} records to {output_path}")

def write_names_to_csv(names_list, output_path):
    """Write name records to CSV and compress with gzip."""
    if not names_list:
        return
    
    # Add .gz extension if not already present
    if not output_path.endswith('.gz'):
        output_path = output_path + '.gz'
    
    # Names CSV has fixed columns
    fieldnames = ['name', 'start_date', 'end_date', 'cik']
    
    # Write directly to gzipped CSV
    with gzip.open(output_path, 'wt', encoding='utf-8', newline='') as gzfile:
        writer = csv.DictWriter(gzfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(names_list)
    
    print(f"Wrote {len(names_list)} records to {output_path}")

async def extract_and_process_metadata(output_dir, local_zip_path=None, sec_url="https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip", max_bytes=2000):
    """
    Extracts metadata from JSON files in a ZIP archive and writes to multiple CSV files.
    Can download the ZIP file from SEC to a temporary location if local_zip_path not provided.
    
    Args:
        output_dir (str): Directory for output CSV files
        local_zip_path (str, optional): Path to a local ZIP file. If None, downloads from SEC to temp
        sec_url (str): URL to download the SEC submissions ZIP file
        max_bytes (int): Maximum number of bytes to extract from each file
    
    Returns:
        dict: Statistics about processed files
    """
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Initialize collections for different types of data
    listed_metadata = []
    unlisted_metadata = []
    listed_names = []
    unlisted_names = []
    
    stats = {
        'total_processed': 0,
        'listed_companies': 0,
        'unlisted_companies': 0,
        'full_content_reads': 0
    }
    
    # Use provided ZIP file or download to temporary file
    if local_zip_path:
        # Use local file
        print(f"Using local ZIP file: {local_zip_path}")
        zip_path = local_zip_path
        temp_file = None
    else:
        # Download to temporary file
        print(f"Downloading from SEC to temporary file: {sec_url}")
        temp_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        temp_file.close()  # Close the file so we can download to it
        zip_path = temp_file.name
        
        try:
            await download_sec_file(sec_url, zip_path)
        except Exception as e:
            # Clean up temp file if download fails
            if os.path.exists(zip_path):
                os.unlink(zip_path)
            raise e
    
    try:
        # Process the ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of files (excluding directories)
            files = [f for f in zip_ref.infolist() if not f.is_dir()]
            # Remove files that contain "submission" in their name
            files = [f for f in files if "submission" not in f.filename]
            # Remove placeholder.txt
            files = [f for f in files if "placeholder.txt" not in f.filename]
            
            
            # Create a progress bar
            with tqdm(total=len(files), desc="Extracting metadata", unit="file") as pbar:
                # Loop through all files in the ZIP archive
                for file_info in files:
                    try:
                        # Initially read just a small chunk of the file
                        with zip_ref.open(file_info.filename, 'r') as file:
                            partial_content_bytes = file.read(max_bytes)
                            
                            # Convert to string
                            partial_content = partial_content_bytes.decode('utf-8', errors='replace')
                            
                            # Truncate at "filings" and complete the JSON for initial parsing
                            filings_index = partial_content.find('"filings":')
                            if filings_index != -1:
                                # Get content up to "filings"
                                truncated_content = partial_content[:filings_index]
                                # Remove trailing comma if present
                                truncated_content = truncated_content.rstrip().rstrip(',')
                                # Add closing brace
                                partial_content = truncated_content + '}'
                            else:
                                # If "filings" not found, try to make valid JSON by adding closing brace
                                partial_content = partial_content.rstrip().rstrip(',') + '}'
                            
                            try:
                                # Parse the partial JSON to check for former names
                                partial_json_data = json.loads(partial_content)
                                
                                # Check if we need full content (no former names or former names is empty list)
                                former_names = partial_json_data.get('formerNames', [])
                                need_full_content = not former_names or len(former_names) == 0
                                
                                # Initialize json_data with the partial data
                                json_data = partial_json_data
                                
                                # If we need more data for filing dates, read the full file
                                if need_full_content:
                                    stats['full_content_reads'] += 1
                                    
                                    # Read the entire file content
                                    with zip_ref.open(file_info.filename, 'r') as full_file:
                                        full_content_bytes = full_file.read()
                                        full_content = full_content_bytes.decode('utf-8', errors='replace')
                                        
                                        try:
                                            # Parse the full JSON
                                            json_data = json.loads(full_content)
                                        except json.JSONDecodeError:
                                            # If full content can't be parsed, stick with partial data
                                            print(f"Warning: Could not parse full content of {file_info.filename}, using partial data")
                                
                                # Extract metadata (without former names)
                                metadata = extract_metadata(json_data)
                                
                                # Get CIK and name for former names processing
                                cik = metadata.get('cik', '')
                                name = metadata.get('name', '')
                                
                                # Process former names with the full json_data
                                # Now also returning the earliest company date
                                former_names_records, earliest_company_date = process_former_names(json_data, cik, name)
                                
                                # Add the earliest company date to the metadata
                                metadata['start_date'] = earliest_company_date if earliest_company_date else ''
                                
                                # Check if company is listed (has tickers)
                                tickers = metadata.get('tickers', [])
                                is_listed = tickers and isinstance(tickers, list) and len(tickers) > 0
                                
                                # Add to appropriate collections
                                if is_listed:
                                    listed_metadata.append(metadata)
                                    listed_names.extend(former_names_records)
                                    stats['listed_companies'] += 1
                                else:
                                    unlisted_metadata.append(metadata)
                                    unlisted_names.extend(former_names_records)
                                    stats['unlisted_companies'] += 1
                                
                                stats['total_processed'] += 1
                                
                            except json.JSONDecodeError as je:
                                print(f"JSON parsing error in {file_info.filename}: {str(je)}")
                    
                    except Exception as e:
                        # Handle any errors
                        print(f"Error processing {file_info.filename}: {str(e)}")
                    
                    # Update the progress bar
                    pbar.update(1)
    
    finally:
        # Clean up temporary file if we created one
        if temp_file and os.path.exists(zip_path):
            print(f"Removing temporary file: {zip_path}")
            os.unlink(zip_path)
    
    # Define output file paths (without .gz extension, it will be added in the write functions)
    listed_metadata_path = os.path.join(output_dir, "listed_filer_metadata.csv")
    unlisted_metadata_path = os.path.join(output_dir, "unlisted_filer_metadata.csv")
    listed_names_path = os.path.join(output_dir, "listed_filer_names.csv")
    unlisted_names_path = os.path.join(output_dir, "unlisted_filer_names.csv")
    
    # Write listed metadata to CSV
    if listed_metadata:
        write_metadata_to_csv(listed_metadata, listed_metadata_path)
    
    # Write unlisted metadata to CSV
    if unlisted_metadata:
        write_metadata_to_csv(unlisted_metadata, unlisted_metadata_path)
    
    # Write listed names to CSV
    if listed_names:
        write_names_to_csv(listed_names, listed_names_path)
    
    # Write unlisted names to CSV
    if unlisted_names:
        write_names_to_csv(unlisted_names, unlisted_names_path)
    
    # Print summary
    print(f"\nTotal files processed: {stats['total_processed']}")
    print(f"Listed companies found: {stats['listed_companies']}")
    print(f"Unlisted companies found: {stats['unlisted_companies']}")
    print(f"Files requiring full content read: {stats['full_content_reads']}")
    print(f"Output files written to {output_dir}")
    
    return stats

# Convenience function to run the extractor
def process_submissions_metadata(output_dir, local_zip_path=None, sec_url="https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip", max_bytes=2000):
    """
    Convenience function to run the SEC Metadata Extractor.
    
    Args:
        output_dir (str): Directory for output CSV files
        local_zip_path (str, optional): Path to a local ZIP file. If None, downloads from SEC to temp
        sec_url (str): URL to download the SEC submissions ZIP file
        max_bytes (int): Maximum number of bytes to extract from each file
    
    Returns:
        dict: Statistics about processed files
    """
    return asyncio.run(extract_and_process_metadata(
        output_dir=output_dir,
        local_zip_path=local_zip_path,
        sec_url=sec_url,
        max_bytes=max_bytes
    ))
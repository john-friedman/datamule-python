import asyncio
import time
from collections import deque
import aiohttp
from lxml import etree
import re
from tqdm.auto import tqdm
from ..utils import RetryException, PreciseRateLimiter, RateMonitor, headers

async def start_monitor(data_callback=None, poll_callback=None, submission_type=None, cik=None,
                        polling_interval=200, requests_per_second=2.0, quiet=True, known_accession_numbers=None):
    """
    Main monitoring loop for SEC filings.
    
    Parameters:
        data_callback (callable): Async function to call when new filings are found.
        poll_callback (callable): Async function to call during polling wait periods.
        submission_type (str or list): Form type(s) to monitor (e.g., "8-K", "10-Q").
        cik (str or list): CIK(s) to monitor.
        polling_interval (int): Polling interval in milliseconds.
        requests_per_second (float): Maximum requests per second.
        quiet (bool): Suppress verbose output.
        known_accession_numbers (list): List of accession numbers to skip (already processed).
    """
    # Initialize rate limiter
    rate_limiter = PreciseRateLimiter(requests_per_second)
    rate_monitor = RateMonitor()
    
    # Initialize known accession numbers with a maximum size of 20,000
    if known_accession_numbers is None:
        known_accession_numbers = deque(maxlen=20000)
    else:
        known_accession_numbers = deque(known_accession_numbers, maxlen=20000)
    
    # Convert submission_type to list if it's a string
    if submission_type and isinstance(submission_type, str):
        submission_type = [submission_type]
    
    # Convert CIK to list if it's a string
    if cik and isinstance(cik, str):
        cik = [cik]
    
    # Set up base URL parameters
    url_params = {
        'action': 'getcurrent',
        'owner': 'include',
        'count': 100,
        'output': 'atom'
    }
    
    if submission_type:
        url_params['type'] = ','.join(submission_type)
    if cik:
        url_params['CIK'] = ','.join(cik)
    
    # Store first page accession numbers for quick polling
    first_page_accession_numbers = set()
    
    # Initialize by loading a batch of the latest filings
    # Pass the data_callback to initialize_known_filings
    await initialize_known_filings(url_params, known_accession_numbers, rate_limiter, rate_monitor, quiet, data_callback)
    
    # Main polling loop
    while True:
        try:
            # Poll for new filings on the first page
            new_filings = await poll_for_new_filings(url_params, first_page_accession_numbers, 
                                                    rate_limiter, rate_monitor, quiet)
            
            if new_filings:
                # If there are new filings, check if we need to fetch more comprehensive data
                if len(new_filings) >= 100:  # If the entire first page is new
                    new_filings = await fetch_comprehensive_filings(url_params, known_accession_numbers, 
                                                                    rate_limiter, rate_monitor, quiet)
                
                # Process new filings and call the data callback
                if new_filings and data_callback:
                    processed_filings = process_filings(new_filings)
                    await data_callback(processed_filings)
                    
                    # Add new filings to known accession numbers
                    for filing in processed_filings:
                        known_accession_numbers.append(filing['accession_number'])
                
                if not quiet:
                    print(f"Found {len(processed_filings)} new filings.")
            
            # Call the poll callback if provided
            # Ensure callback output gets its own line and doesn't mix with other messages
            if poll_callback:
                await poll_callback()
            
            # Wait for the next polling interval
            await asyncio.sleep(polling_interval / 1000.0)  # Convert milliseconds to seconds
            
        except RetryException as e:
            if not quiet:
                print(f"Rate limit exceeded. Retrying after {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            if not quiet:
                print(f"Error in monitoring loop: {e}")
            await asyncio.sleep(polling_interval / 1000.0)  # Wait before retrying

async def initialize_known_filings(url_params, known_accession_numbers, rate_limiter, rate_monitor, quiet, data_callback=None):
    """Initialize the list of known accession numbers from the SEC feed."""
    if not quiet:
        print("Initializing known filings...")
    
    # Fetch a large batch of filings to initialize
    all_filings = await fetch_comprehensive_filings(url_params, set(), rate_limiter, rate_monitor, quiet)
    
    # Process and emit filings if data_callback is provided
    if data_callback and all_filings:
        processed_filings = process_filings(all_filings)
        if not quiet:
            print(f"Emitting {len(processed_filings)} initial filings to data callback...")
        await data_callback(processed_filings)
    
    # Add all fetched accession numbers to the known list
    if not quiet:
        # Create a single progress bar that stays in place and shows rate
        with tqdm(total=len(all_filings), desc="Processing filings", unit="filing", ncols=100, 
                 leave=False, position=0, 
                 bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
            for filing in all_filings:
                acc_no = extract_accession_number(filing)
                if acc_no:
                    known_accession_numbers.append(acc_no)
                pbar.update(1)
    else:
        for filing in all_filings:
            acc_no = extract_accession_number(filing)
            if acc_no:
                known_accession_numbers.append(acc_no)
    
    if not quiet:
        print(f"Initialized with {len(known_accession_numbers)} known filings.")

async def poll_for_new_filings(url_params, first_page_accession_numbers, rate_limiter, rate_monitor, quiet):
    """Poll the first page of SEC filings to check for new ones."""
    # Create a copy of the URL parameters for the first page
    page_params = url_params.copy()
    page_params['start'] = 0
    
    # Construct the URL
    url = construct_url(page_params)
    
    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            if not quiet:
                # Use a clear line break before polling message
                print(f"Polling {url}")
            
            async with session.get(url, headers=headers) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 601))
                    raise RetryException(url, retry_after)
                
                content = await response.read()
                await rate_monitor.add_request(len(content))
                
                if response.status != 200:
                    if not quiet:
                        print(f"Error {response.status} from SEC API: {content}")
                    return []
                
                # Parse the XML response
                root = etree.fromstring(content)
                entries = root.xpath("//xmlns:entry", namespaces={"xmlns": "http://www.w3.org/2005/Atom"})
                
                # Extract accession numbers from entries
                current_accession_numbers = set()
                for entry in entries:
                    acc_no = extract_accession_number(entry)
                    if acc_no:
                        current_accession_numbers.add(acc_no)
                
                # Check for new accession numbers
                if not first_page_accession_numbers:
                    # First run, just store the current accession numbers
                    first_page_accession_numbers.update(current_accession_numbers)
                    return []
                
                # Find new accession numbers
                new_accession_numbers = current_accession_numbers - first_page_accession_numbers
                
                # Update first page accession numbers
                first_page_accession_numbers.clear()
                first_page_accession_numbers.update(current_accession_numbers)
                
                # If there are new accession numbers, return ALL entries with those numbers
                if new_accession_numbers:
                    new_entries = []
                    for entry in entries:
                        acc_no = extract_accession_number(entry)
                        if acc_no and acc_no in new_accession_numbers:
                            new_entries.append(entry)
                    return new_entries
                
                return []

async def fetch_comprehensive_filings(url_params, known_accession_numbers, rate_limiter, rate_monitor, quiet):
    """Fetch a comprehensive list of filings, potentially paginating through multiple requests."""
    all_new_filings = []
    
    # We'll fetch up to 2000 filings in batches of 100
    page_range = range(0, 2000, 100)
    
    # Create a single progress bar that stays in place and shows rate
    pbar = None
    if not quiet:
        # Use a custom format that includes rate (pages/sec)
        pbar = tqdm(total=len(page_range), desc="Fetching pages", unit="page", ncols=100, 
                   leave=False, position=0, 
                   bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]')
    
    fetch_status = ""
    try:
        for start in page_range:
            if pbar:
                pbar.update(1)

            page_params = url_params.copy()
            page_params['start'] = start
            
            url = construct_url(page_params)
            
            if not quiet:
                fetch_status = f"Fetching {url}"
                if pbar:
                    # Add URL to the progress bar but keep it short
                    pbar.set_postfix_str(fetch_status[:30] + "..." if len(fetch_status) > 30 else fetch_status)
                    # Ensure the progress bar gets displayed with the current rate
                    pbar.refresh()
            
            async with aiohttp.ClientSession() as session:
                async with rate_limiter:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 429:
                            retry_after = int(response.headers.get('Retry-After', 601))
                            raise RetryException(url, retry_after)
                        
                        content = await response.read()
                        await rate_monitor.add_request(len(content))
                        
                        if response.status != 200:
                            if not quiet:
                                print(f"Error {response.status} from SEC API: {content}")
                            break
                        
                        # Parse the XML response
                        root = etree.fromstring(content)
                        entries = root.xpath("//xmlns:entry", namespaces={"xmlns": "http://www.w3.org/2005/Atom"})
                        
                        if not entries:
                            # No more entries, stop pagination
                            break
                        
                        # Check for new filings - collect all entries, not just one per accession number
                        for entry in entries:
                            acc_no = extract_accession_number(entry)
                            if acc_no and acc_no not in known_accession_numbers:
                                all_new_filings.append(entry)
                        
                        if len(entries) < 100:
                            # Less than a full page, no need to continue pagination
                            break
    finally:
        # Always close the progress bar
        if pbar:
            pbar.close()
    
    return all_new_filings

def process_filings(filings):
    """
    Process a list of filing entries and return structured data.
    Combines entries with the same accession number and collects all CIKs.
    """
    # Group filings by accession number
    filing_groups = {}
    
    for filing in filings:
        acc_no = extract_accession_number(filing)
        if not acc_no:
            continue
        
        # Get submission type
        submission_type = extract_submission_type(filing)
        
        # Get CIK
        cik = extract_cik(filing)
        
        # Initialize or update the filing group
        if acc_no not in filing_groups:
            filing_groups[acc_no] = {
                'accession_number': acc_no,
                'submission_type': submission_type,
                'ciks': []
            }
        
        # Add CIK if it's not already in the list and is valid
        if cik and cik not in filing_groups[acc_no]['ciks']:
            filing_groups[acc_no]['ciks'].append(cik)
    
    # Convert the dictionary to a list of filing dictionaries
    return list(filing_groups.values())

def extract_accession_number(entry):
    """Extract the accession number from an entry."""
    id_element = entry.find(".//xmlns:id", namespaces={"xmlns": "http://www.w3.org/2005/Atom"})
    if id_element is not None and id_element.text:
        match = re.search(r'accession-number=(\d+-\d+-\d+)', id_element.text)
        if match:
            return match.group(1)
    return None

def extract_submission_type(entry):
    """Extract the submission type from an entry."""
    category_element = entry.find(".//xmlns:category", namespaces={"xmlns": "http://www.w3.org/2005/Atom"})
    if category_element is not None:
        return category_element.get('term')
    return None

def extract_cik(entry):
    """Extract the CIK from an entry's link URL."""
    link_element = entry.find(".//xmlns:link", namespaces={"xmlns": "http://www.w3.org/2005/Atom"})
    if link_element is not None and 'href' in link_element.attrib:
        href = link_element.get('href')
        match = re.search(r'/data/(\d+)/', href)
        if match:
            return match.group(1)
    return None

def construct_url(params):
    """Construct a URL with the given parameters."""
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{query_string}"

def monitor(data_callback=None, poll_callback=None, submission_type=None, cik=None, 
           polling_interval=200, requests_per_second=2.0, quiet=True, known_accession_numbers=None):
    """
    Convenience function to start monitoring SEC filings from the RSS feed.
    
    Parameters:
        data_callback (callable): Async function to call when new filings are found.
                                 Will be called with a list of dicts containing
                                 'accession_number', 'submission_type', and 'ciks'.
        poll_callback (callable): Async function to call during polling wait periods.
        submission_type (str or list): Form type(s) to monitor (e.g., "8-K", "10-Q").
        cik (str or list): CIK(s) to monitor.
        polling_interval (int): Polling interval in milliseconds.
        requests_per_second (float): Maximum requests per second.
        quiet (bool): Suppress verbose output.
        known_accession_numbers (list): List of accession numbers to skip (already processed).
    """
    return asyncio.run(start_monitor(
        data_callback=data_callback,
        poll_callback=poll_callback,
        submission_type=submission_type,
        cik=cik,
        polling_interval=polling_interval,
        requests_per_second=requests_per_second,
        quiet=quiet,
        known_accession_numbers=known_accession_numbers
    ))
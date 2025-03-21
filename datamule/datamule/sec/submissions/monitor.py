import asyncio
from datetime import datetime, timedelta
from .eftsquery import EFTSQuery  # Import the class directly instead of the function
from ..rss.monitor import start_monitor  # Import start_monitor directly
import pytz


async def _process_efts_hits(hits, collected_accession_numbers, data_callback=None):
    """Process EFTS hits, collect accession numbers, and call data callback."""
    processed_hits = []
    
    for hit in hits:
        try:
            source = hit.get('_source', {})
            
            # Extract key fields
            accession_number = source.get('adsh')
                
            # Extract submission_type (form) and ciks
            submission_type = source.get('form')
            ciks = source.get('ciks', [])
            ciks = [str(int(cik)) for cik in ciks]
                
            # Create standardized filing record
            filing = {
                'accession_number': accession_number,
                'submission_type': submission_type,
                'ciks': ciks
            }
            
            processed_hits.append(filing)
            collected_accession_numbers.add(accession_number)  # Changed append to add for set operation
            
        except Exception as e:
            print(f"Error processing EFTS hit: {e}")
    
    # Call data callback if provided
    if data_callback and processed_hits:
        await data_callback(processed_hits)
        
    return processed_hits

async def _master_monitor_impl(data_callback=None, poll_callback=None, submission_type=None, cik=None, 
                              polling_interval=200, requests_per_second=2.0, quiet=True, start_date=None):
    """Implementation of the master monitor."""
    # Set default start date to today if not provided (eastern)
    eastern_tz = pytz.timezone('US/Eastern')
    current_date = datetime.now(eastern_tz).strftime('%Y-%m-%d')
    if not start_date:
        start_date = current_date
        
    # Changed from list to set for more efficient lookups
    collected_accession_numbers = set()
    
    if not quiet:
        print(f"Starting SEC monitoring from {start_date}")
    
    # Step 1: Query EFTS for all filings from start_date up to current date
    if not quiet:
        print(f"Fetching filings from {start_date} to {current_date}...")
    
    # Prepare a wrapper callback to collect accession numbers
    async def process_callback(hits):
        await _process_efts_hits(hits, collected_accession_numbers, data_callback)
    
    # Create an EFTSQuery instance
    efts_query = EFTSQuery(requests_per_second=requests_per_second)
    
    # Run EFTS query for the date range
    async with efts_query:
        await efts_query.query(
            cik=cik,
            submission_type=submission_type,
            filing_date=(start_date, current_date),
            callback=process_callback
        )
    
    if not quiet:
        print(f"Historical query complete. Collected {len(collected_accession_numbers)} accession numbers.")
    
    # Step 2: Hand off to RSS monitor with collected accession numbers
    if not quiet:
        print("Starting real-time RSS monitoring...")
    
    # Start RSS monitor with the set of accession numbers to skip (from EFTS)
    # and an empty list for ongoing tracking
    await start_monitor(
        data_callback=data_callback,
        poll_callback=poll_callback,
        submission_type=submission_type,
        cik=cik,
        polling_interval=polling_interval,
        requests_per_second=requests_per_second,
        quiet=quiet,
        known_accession_numbers=[],  # Start with an empty list for ongoing tracking
        skip_initial_accession_numbers=collected_accession_numbers  # Pass the EFTS accession numbers as the skip list
    )

def monitor(data_callback=None, poll_callback=None, submission_type=None, cik=None, 
           polling_interval=200, requests_per_second=2.0, quiet=True, start_date=None):
    """
    Monitor SEC filings by combining EFTS historical queries with real-time RSS monitoring.
    
    Parameters:
        data_callback (callable): Async function to call when new filings are found.
                                 Will be called with a list of dicts containing
                                 'accession_number', 'submission_type', and 'ciks'.
        poll_callback (callable): Async function to call during RSS polling wait periods.
        submission_type (str or list): Form type(s) to monitor (e.g., "8-K", "10-Q").
        cik (str or list): CIK(s) to monitor.
        polling_interval (int): Polling interval in milliseconds for RSS monitor.
        requests_per_second (float): Maximum requests per second.
        quiet (bool): Suppress verbose output.
        start_date (str): ISO format date (YYYY-MM-DD) from which to start monitoring.
                        If None, will start from current date. (EASTERN TIME)
    """
    return asyncio.run(_master_monitor_impl(
        data_callback=data_callback,
        poll_callback=poll_callback,
        submission_type=submission_type,
        cik=cik,
        polling_interval=polling_interval,
        requests_per_second=requests_per_second,
        quiet=quiet,
        start_date=start_date
    ))
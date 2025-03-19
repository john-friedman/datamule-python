import asyncio
import aiohttp
from datetime import datetime, timedelta
import pytz
import time
from collections import deque
from ..utils import PreciseRateLimiter, RateMonitor, RetryException, headers
from .eftsquery import EFTSQuery

def _get_current_eastern_date():
    """Get current date in US Eastern timezone (automatically handles DST)"""
    eastern = pytz.timezone('America/New_York')
    return datetime.now(eastern)

def _parse_date(date_str):
    """Parse YYYY-MM-DD date string to datetime object in Eastern timezone"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        eastern = pytz.timezone('America/New_York')
        return eastern.localize(date)
    except ValueError as e:
        raise ValueError(f"Invalid date format. Please use YYYY-MM-DD. Error: {str(e)}")

def _extract_accession_number(filing_id):
    """Extract accession number from filing ID by splitting at colon and taking first part"""
    if filing_id and ':' in filing_id:
        return filing_id.split(':', 1)[0]
    return filing_id  # Return original if no colon found

class Monitor:
    def __init__(self):
        self.recent_accession_numbers = deque(maxlen=10000)  # Limit to recent 10,000 accessions
        self.current_monitor_date = None  # Current date being monitored
        self.max_hits = 10000  # Maximum filings to retrieve
        self.limiter = None  # Will be initialized in monitor method
        self.rate_monitor = RateMonitor()  # Track request rates
        self.headers = headers  # User agent headers
        self.date_accessions = {}  # Track accessions by date during backfill

    async def _fetch_json(self, session, url):
        """Fetch JSON with rate limiting and monitoring."""
        async with self.limiter:
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    content = await response.read()
                    await self.rate_monitor.add_request(len(content))
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Rate limit exceeded
                    retry_after = int(e.headers.get('Retry-After', 601))
                    raise RetryException(url, retry_after)
                raise
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
                return None

    async def _poll(self, base_url, session, poll_interval, quiet, poll_callback):
        """Poll API until new submissions are found."""
        current_date = _get_current_eastern_date()
        
        # If we're caught up to current date, use it, otherwise use our tracking date
        if self.current_monitor_date.date() >= current_date.date():
            self.current_monitor_date = current_date
        else:
            # Move to next day if needed
            if not self.date_accessions.get(self.current_monitor_date.strftime('%Y-%m-%d'), set()):
                # No filings seen for current date, move to next
                self.current_monitor_date += timedelta(days=1)
                
        date_str = self.current_monitor_date.strftime('%Y-%m-%d')
        timestamp = int(time.time())
        
        # Construct poll URL
        poll_url = f"{base_url}&startdt={date_str}&enddt={date_str}&v={timestamp}"
        if not quiet:
            print(f"Polling {poll_url}")
        
        # Fetch first page
        try:
            data = await self._fetch_json(session, poll_url)
            if data and 'hits' in data and 'hits' in data['hits']:
                # Process filings in this page
                new_filings = []
                has_new_filings = False
                
                for filing in data['hits']['hits']:
                    accession = _extract_accession_number(filing['_id'])
                    
                    # Check if this filing is new
                    if accession not in self.recent_accession_numbers:
                        has_new_filings = True
                        self.recent_accession_numbers.append(accession)
                        new_filings.append(filing)
                        
                        # Also track by date for date transitions
                        if date_str not in self.date_accessions:
                            self.date_accessions[date_str] = set()
                        self.date_accessions[date_str].add(accession)
                
                # If we have new filings, check if we need pagination
                if has_new_filings:
                    if not quiet:
                        print(f"Found {len(new_filings)} new filings")
                    
                    # Determine if we need pagination - if all filings in this page were new
                    # and there are more pages, we need to paginate
                    need_pagination = len(new_filings) == len(data['hits']['hits']) and len(data['hits']['hits']) > 0
                    return need_pagination, data, poll_url, new_filings
                
                # If no hits and we're processing a past date,
                # we can move to the next day immediately
                if len(data['hits']['hits']) == 0 and self.current_monitor_date.date() < current_date.date():
                    self.current_monitor_date += timedelta(days=1)
                    # Clear accessions for dates older than the current monitor date
                    self._clear_old_date_accessions()
                    return False, None, None, []
                
        except RetryException as e:
            print(f"Rate limit exceeded. Retrying after {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after)
            return False, None, None, []
        except Exception as e:
            print(f"Error in poll: {str(e)}")
        
        # Execute polling callback if provided
        start_wait = time.time()
        if poll_callback:
            try:
                await poll_callback()
            except Exception as e:
                print(f"Error in poll callback: {str(e)}")
        
        # Check if polling callback took longer than polling interval
        elapsed = (time.time() - start_wait) * 1000
        if elapsed < poll_interval:
            await asyncio.sleep((poll_interval - elapsed) / 1000)
        
        return False, None, None, []

    def _clear_old_date_accessions(self):
        """Clear accessions for dates older than the current monitor date."""
        current_date_str = self.current_monitor_date.strftime('%Y-%m-%d')
        keys_to_remove = [key for key in self.date_accessions.keys() if key < current_date_str]
        for key in keys_to_remove:
            del self.date_accessions[key]

    async def _retrieve_batch(self, session, poll_url, from_positions, quiet):
        """Retrieve a batch of submissions concurrently."""
        tasks = [
            self._fetch_json(
                session,
                f"{poll_url}&from={pos}"
            )
            for pos in from_positions
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_filings = []
        new_filings = []
        date_str = self.current_monitor_date.strftime('%Y-%m-%d')
        
        for result in results:
            if isinstance(result, Exception):
                if isinstance(result, RetryException):
                    print(f"Rate limit exceeded. Retrying after {result.retry_after} seconds.")
                    await asyncio.sleep(result.retry_after)
                else:
                    print(f"Error in batch: {str(result)}")
                continue
            if result and 'hits' in result and 'hits' in result['hits']:
                filings = result['hits']['hits']
                all_filings.extend(filings)
                
                # Process filings for new ones
                for filing in filings:
                    accession = _extract_accession_number(filing['_id'])
                    if accession not in self.recent_accession_numbers:
                        self.recent_accession_numbers.append(accession)
                        new_filings.append(filing)
                        
                        # Also track by date
                        if date_str not in self.date_accessions:
                            self.date_accessions[date_str] = set()
                        self.date_accessions[date_str].add(accession)
        
        return all_filings, new_filings

    async def _retrieve_all_pages(self, poll_url, initial_data, session, quiet, first_page_new_filings):
        """Retrieve all filings using parallel batch processing."""
        batch_size = 10  # Number of concurrent requests
        page_size = 100  # Results per request
        total_hits = initial_data['hits']['total']['value']
        max_position = min(self.max_hits, total_hits)
        all_new_filings = first_page_new_filings.copy()  # Start with new filings from first page
        
        # If all filings are already processed, return early
        if len(first_page_new_filings) == 0 and len(initial_data['hits']['hits']) > 0:
            return all_new_filings
        
        # Limit to only retrieve additional pages if we found new filings in the first page
        if len(first_page_new_filings) > 0:
            # Process in batches of concurrent requests, starting from position 100
            # (since we already have the first page)
            for batch_start in range(page_size, max_position, batch_size * page_size):
                from_positions = [
                    pos for pos in range(
                        batch_start,
                        min(batch_start + batch_size * page_size, max_position),
                        page_size
                    )
                ]
                
                if not quiet:
                    print(f"Retrieving batch from positions: {from_positions}")
                
                _, batch_new_filings = await self._retrieve_batch(
                    session, poll_url, from_positions, quiet
                )
                
                if not batch_new_filings:
                    # If we got a batch with no new filings, we can stop
                    break
                    
                all_new_filings.extend(batch_new_filings)
                
                # If we got fewer new filings than positions requested, we're likely done
                if len(batch_new_filings) < len(from_positions) * page_size:
                    break
            
        return all_new_filings

    async def _backfill_from_date(self, start_date, data_callback, submission_type=None, cik=None, 
                                requests_per_second=2.0, quiet=True):
        """Backfill data from start_date to yesterday, then today separately."""
        if not quiet:
            print(f"Starting historical backfill from {start_date}")
        
        # Parse the provided start date
        eastern = pytz.timezone('America/New_York')
        try:
            parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d')
            parsed_start_date = eastern.localize(parsed_start_date)
        except ValueError as e:
            raise ValueError(f"Invalid start_date format. Please use YYYY-MM-DD. Error: {str(e)}")
        
        # Current date and yesterday in Eastern time
        current_date = _get_current_eastern_date()
        yesterday = current_date - timedelta(days=1)
        
        # Skip backfill if start_date is today
        if parsed_start_date.date() >= current_date.date():
            return
        
        # Create query client
        query = EFTSQuery(requests_per_second=requests_per_second)
        
        # Clear and initialize date-specific accessions for backfill
        self.date_accessions = {}
        
        # Define callback function to process backfill results by date
        async def backfill_callback(hits):
            # Group filings by date
            date_filings = {}
            for filing in hits:
                accession = _extract_accession_number(filing['_id'])
                file_date = filing['_source'].get('file_date', '')
                
                # Initialize date entry if needed
                if file_date not in date_filings:
                    date_filings[file_date] = []
                
                # Initialize date accessions if needed
                if file_date not in self.date_accessions:
                    self.date_accessions[file_date] = set()
                
                # Check if this filing is new for this date
                if accession not in self.date_accessions[file_date]:
                    self.date_accessions[file_date].add(accession)
                    self.recent_accession_numbers.append(accession)
                    date_filings[file_date].append(filing)
            
            # Process filings by date, sorted chronologically
            for date in sorted(date_filings.keys()):
                if date_filings[date] and data_callback:
                    # Sort by accession number (which approximates filing time)
                    sorted_data = sorted(date_filings[date], key=lambda x: _extract_accession_number(x['_id']))
                    await data_callback(sorted_data)
        
        # Phase 1: Historical data from start_date to yesterday
        if parsed_start_date.date() < yesterday.date():
            if not quiet:
                print(f"Phase 1: Fetching historical data from {start_date} to {yesterday.strftime('%Y-%m-%d')}")
            
            filing_date = (start_date, yesterday.strftime('%Y-%m-%d'))
            await query.query(
                cik=cik, 
                submission_type=submission_type,
                filing_date=filing_date,
                callback=backfill_callback
            )
        
        # Phase 2: Current day's data
        # This captures anything that might have been published while we were doing Phase 1
        if not quiet:
            print(f"Phase 2: Fetching today's data")
        
        today_str = current_date.strftime('%Y-%m-%d')
        await query.query(
            cik=cik, 
            submission_type=submission_type,
            filing_date=today_str,
            callback=backfill_callback
        )
        
        if not quiet:
            print(f"Historical backfill complete. {len(self.recent_accession_numbers)} filings processed.")

    async def _monitor(self, data_callback, poll_callback, submission_type=None, cik=None, 
                      poll_interval=1000, requests_per_second=5, quiet=True, start_date=None):
        """Main monitoring loop with optional historical backfill."""
        # Initialize rate limiter
        self.limiter = PreciseRateLimiter(requests_per_second)
        
        # Perform historical backfill if start_date is provided
        if start_date:
            await self._backfill_from_date(
                start_date=start_date,
                data_callback=data_callback,
                submission_type=submission_type,
                cik=cik,
                requests_per_second=requests_per_second,
                quiet=quiet
            )
        
        # Set up initial monitoring date
        self.current_monitor_date = _get_current_eastern_date()
        
        # Handle submission_type parameter
        if submission_type is None:
            submission_type = ['-0']  # Default to all forms
        elif isinstance(submission_type, str):
            submission_type = [submission_type]
        
        # Handle CIK parameter
        cik_param = ""
        if cik is not None:
            if isinstance(cik, list):
                cik_list = ','.join(str(c).zfill(10) for c in cik)
            else:
                cik_list = str(cik).zfill(10)
            cik_param = f"&ciks={cik_list}"
        
        # Construct base URL
        base_url = 'https://efts.sec.gov/LATEST/search-index?forms=' + ','.join(submission_type) + cik_param
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            while True:
                try:
                    # Poll until we find new filings
                    need_pagination, data, poll_url, first_page_new_filings = await self._poll(
                        base_url, session, poll_interval, quiet, poll_callback
                    )
                    
                    if data is None:
                        continue  # No new data, continue polling
                    
                    # Process new filings if found
                    all_new_filings = first_page_new_filings
                    
                    if need_pagination:
                        # Need to retrieve additional pages
                        all_new_filings = await self._retrieve_all_pages(
                            poll_url, data, session, quiet, first_page_new_filings
                        )
                    
                    # Call data callback with new filings
                    if all_new_filings and data_callback:
                        await data_callback(all_new_filings)
                    
                except Exception as e:
                    print(f"Error in monitor: {str(e)}")
                    await asyncio.sleep(poll_interval / 1000)

async def start_monitor(data_callback=None, poll_callback=None, submission_type=None, cik=None, 
                      poll_interval=1000, requests_per_second=5, quiet=True, start_date=None):
    """Start the SEC filings monitor with the specified parameters."""
    monitor = Monitor()
    await monitor._monitor(
        data_callback=data_callback,
        poll_callback=poll_callback,
        submission_type=submission_type, 
        cik=cik,
        poll_interval=poll_interval,
        requests_per_second=requests_per_second,
        quiet=quiet,
        start_date=start_date
    )

def monitor(data_callback=None, poll_callback=None, submission_type=None, cik=None, 
           poll_interval=200, requests_per_second=2.0, quiet=True, start_date=None):
    """
    Convenience function to start monitoring SEC filings.
    
    Parameters:
        data_callback (callable): Function to call when new filings are found
        poll_callback (callable): Function to call during polling wait periods
        submission_type (str or list): Form type(s) to monitor (e.g., "8-K", "10-Q")
        cik (str or list): CIK(s) to monitor
        poll_interval (int): Polling interval in milliseconds
        requests_per_second (float): Maximum requests per second
        quiet (bool): Suppress verbose output
        start_date (str): Optional start date for historical backfill (YYYY-MM-DD)
    """
    return asyncio.run(start_monitor(
        data_callback=data_callback,
        poll_callback=poll_callback,
        submission_type=submission_type,
        cik=cik,
        poll_interval=poll_interval,
        requests_per_second=requests_per_second,
        quiet=quiet,
        start_date=start_date
    ))
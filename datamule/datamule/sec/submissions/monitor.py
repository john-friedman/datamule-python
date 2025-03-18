import asyncio
import aiohttp
from datetime import datetime, timedelta
import pytz
import time
from typing import Callable, List, Set, Dict, Any, Optional, Union
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

class Monitor:
    def __init__(self):
        self.seen_filing_ids = set()  # Track all seen filing IDs
        self.current_monitor_date = None  # Current date being monitored
        self.max_hits = 10000  # Maximum filings to retrieve
        self.limiter = None  # Will be initialized in monitor method
        self.rate_monitor = RateMonitor()  # Track request rates
        self.headers = headers  # User agent headers

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
            if not self.seen_filing_ids:  # No filings seen for current date, move to next
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
                # Extract filing IDs from current page
                current_page_ids = {filing['_id'] for filing in data['hits']['hits']}
                
                # Find new filings
                new_ids = current_page_ids - self.seen_filing_ids
                
                # If we have new filings, return them
                if new_ids:
                    need_pagination = len(new_ids) == len(current_page_ids)
                    return need_pagination, data, poll_url
                
                # If no hits and we're processing a past date,
                # we can move to the next day immediately
                if len(current_page_ids) == 0 and self.current_monitor_date.date() < current_date.date():
                    self.current_monitor_date += timedelta(days=1)
                    return False, None, None
                
        except RetryException as e:
            print(f"Rate limit exceeded. Retrying after {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after)
            return False, None, None
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
        
        return False, None, None

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
        filings = []
        
        for result in results:
            if isinstance(result, Exception):
                if isinstance(result, RetryException):
                    print(f"Rate limit exceeded. Retrying after {result.retry_after} seconds.")
                    await asyncio.sleep(result.retry_after)
                else:
                    print(f"Error in batch: {str(result)}")
                continue
            if result and 'hits' in result and 'hits' in result['hits']:
                filings.extend(result['hits']['hits'])
        
        return filings

    async def _retrieve_all_pages(self, poll_url, initial_data, session, quiet):
        """Retrieve all filings using parallel batch processing."""
        batch_size = 10  # Number of concurrent requests
        page_size = 100  # Results per request
        total_hits = initial_data['hits']['total']['value']
        max_position = min(self.max_hits, total_hits)
        all_filings = initial_data['hits']['hits'].copy()  # Start with first page
        
        # Process in batches of concurrent requests, starting from position 100
        # (since we already have the first page from initial_data)
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
            
            batch_filings = await self._retrieve_batch(
                session, poll_url, from_positions, quiet
            )
            
            if not batch_filings:
                break
                
            all_filings.extend(batch_filings)
            
            # If we got fewer results than expected, we're done
            if len(batch_filings) < len(from_positions) * page_size:
                break
        
        # Find new filings
        new_filings = [filing for filing in all_filings if filing['_id'] not in self.seen_filing_ids]
        
        # Update seen IDs
        self.seen_filing_ids.update(filing['_id'] for filing in all_filings)
        
        return new_filings

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
        
        # Prepare backfill data for callback
        backfill_data = []
        
        # Define callback function to process backfill results
        async def backfill_callback(hits):
            for filing in hits:
                filing_id = filing['_id']
                if filing_id not in self.seen_filing_ids:
                    self.seen_filing_ids.add(filing_id)
                    backfill_data.append(filing)
            
            # If we've accumulated enough data or this is the last batch, process it
            if len(backfill_data) >= 100 or len(hits) < 100:
                if backfill_data and data_callback:
                    # Sort by filing date (assuming accession_number order approximates filing time)
                    sorted_data = sorted(backfill_data, key=lambda x: x['_id'])
                    if not quiet:
                        print(f"Processing batch of {len(sorted_data)} historical filings")
                    await data_callback(sorted_data)
                    backfill_data.clear()
        
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
        
        # Process any remaining data
        if backfill_data and data_callback:
            sorted_data = sorted(backfill_data, key=lambda x: x['_id'])
            if not quiet:
                print(f"Processing final batch of {len(sorted_data)} historical filings")
            await data_callback(sorted_data)
        
        if not quiet:
            print(f"Historical backfill complete. {len(self.seen_filing_ids)} filings processed.")

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
                    need_pagination, data, poll_url = await self._poll(
                        base_url, session, poll_interval, quiet, poll_callback
                    )
                    
                    if data is None:
                        continue  # No new data, continue polling
                    
                    # Process new filings
                    if need_pagination:
                        # Need to retrieve all pages - complete set change detected
                        new_filings = await self._retrieve_all_pages(poll_url, data, session, quiet)
                    else:
                        # Just process new filings from first page
                        first_page_filings = data['hits']['hits']
                        new_filings = [f for f in first_page_filings if f['_id'] not in self.seen_filing_ids]
                        # Update seen IDs
                        self.seen_filing_ids.update(f['_id'] for f in first_page_filings)
                    
                    # Call data callback with new filings
                    if new_filings and data_callback:
                        await data_callback(new_filings)
                    
                    # Output current rates
                    reqs_per_sec, mb_per_sec = self.rate_monitor.get_current_rates()
                    if not quiet:
                        print(f"Current rates: {reqs_per_sec} req/s, {mb_per_sec} MB/s")
                    
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
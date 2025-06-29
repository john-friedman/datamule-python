import time
from collections import deque
from datetime import datetime
import xml.etree.ElementTree as ET
import re
import asyncio
from ..utils import headers, PreciseRateLimiter
from .eftsquery import EFTSQuery
import aiohttp
from zoneinfo import ZoneInfo 

async def poll_rss(limiter, session):
    base_url = 'https://www.sec.gov/cgi-bin/browse-edgar?count=100&action=getcurrent&output=rss'
    
    # Use the rate limiter before making the request
    async with limiter:
        # Use the provided session instead of creating a new one
        async with session.get(base_url) as response:
            content = await response.read()
    
    # Process the content
    content_str = content.decode('utf-8')
    root = ET.fromstring(content_str)
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    entries = root.findall('atom:entry', namespace)
    grouped = {}

    for entry in entries:
        url = entry.find('atom:link', namespace).get('href')
        accession = re.search(r'/(\d{10})-(\d{2})-(\d{6})', url)
        accession = accession.group(1) + accession.group(2) + accession.group(3)
        cik = re.search(r'/data/(\d+)/', url).group(1)
        
        if accession not in grouped:
            grouped[accession] = {'submission_type': '', 'ciks': set(), 'filing_date': ''}
        
        grouped[accession]['ciks'].add(cik)
        grouped[accession]['submission_type'] = entry.find('atom:category', namespace).get('term')
        summary_text = entry.find('atom:summary', namespace).text
        filing_date_match = re.search(r'Filed:</b>\s*(\d{4}-\d{2}-\d{2})', summary_text)
        if filing_date_match:
            grouped[accession]['filing_date'] = filing_date_match.group(1)

    results = [{'accession': int(k.replace('-', '')), 'submission_type': v['submission_type'], 'ciks': list(v['ciks']), 'filing_date': v['filing_date']} for k, v in grouped.items()]
    return results

def clean_efts_hits(hits):
    # clean hits and standardize CIKs to string(int)
    cleaned_hits = []
    for hit in hits:
        # Get CIKs from the source, ensure it's a list
        raw_ciks = hit['_source'].get('ciks', []) 
        
        # Standardize each CIK: convert to int (removes leading zeros) then back to string
        standardized_ciks = [str(int(cik)) for cik in raw_ciks if cik.isdigit()] # Added .isdigit() for robustness
        
        cleaned_hits.append({
            'accession': int(hit['_source']['adsh'].replace('-','')),
            'filing_date': hit['_source']['file_date'],
            'ciks': standardized_ciks, # Use the standardized CIKs here
            'submission_type': hit['_source']['file_type']
        })
    return cleaned_hits

class Monitor():
    def __init__(self):
        self.accessions = deque(maxlen=50000)
        self.accessions_set = set()
        self.ratelimiters = {'sec.gov': PreciseRateLimiter(rate=5)}
        self.efts_query = EFTSQuery(quiet=True)
        self.efts_query.limiter = self.ratelimiters['sec.gov']
        self.session = None
        self.session_created_at = 0
        self.session_lifetime = 300  # 5 minutes in seconds

    def set_domain_rate_limit(self, domain, rate):
        self.ratelimiters[domain] = PreciseRateLimiter(rate=rate)
        if domain == 'sec.gov':
            self.efts_query.limiter = self.ratelimiters[domain]
    
    async def _ensure_fresh_session(self):
        """Ensure we have a fresh session, recreating if expired or missing"""
        current_time = time.time()
        
        # Check if we need a new session
        if (self.session is None or 
            current_time - self.session_created_at > self.session_lifetime):
            
            # Close old session if it exists
            if self.session:
                await self.session.close()
            
            # Create new session
            self.session = aiohttp.ClientSession(headers=headers)
            self.session_created_at = current_time
    
    async def _async_run_efts_query(self, **kwargs):
        """Async helper method to run EFTS query without creating a new event loop"""
        # Make sure to set quiet parameter if provided in kwargs
        self.efts_query.quiet = kwargs.get('quiet', True)
        return await self.efts_query.query(
            cik=kwargs.get('cik'), 
            submission_type=kwargs.get('submission_type'),
            filing_date=kwargs.get('filing_date'),
            location=kwargs.get('location'),
            callback=kwargs.get('callback'),
            name=kwargs.get('name')
        )

    async def _async_monitor_submissions(self, data_callback=None, interval_callback=None,
                        polling_interval=1000, quiet=True, start_date=None,
                        validation_interval=60000):
        """
        Async implementation of monitor_submissions.
        Either polling_interval or validation_interval (or both) must be specified.
        If polling_interval is None, only EFTS validation will be performed.
        If validation_interval is None, only RSS polling will be performed.
        """

        # Validate that at least one interval is specified
        if polling_interval is None and validation_interval is None:
            raise ValueError("At least one of polling_interval or validation_interval must be specified")

        # Ensure we have a fresh session
        await self._ensure_fresh_session()
        
        try:
            # Backfill if start_date is provided
            if start_date is not None:
                today_date = datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%d')
                if not quiet:
                    print(f"Backfilling from {start_date} to {today_date}")

                hits = clean_efts_hits(await self._async_run_efts_query(
                    filing_date=(start_date, today_date),
                    quiet=quiet
                ))

                new_hits = self._filter_new_accessions(hits)
                if not quiet:
                    print(f"New submissions found: {len(new_hits)}")
                if new_hits and data_callback:
                    data_callback(new_hits)

            # Initialize timing variables
            current_time = time.time()
            last_polling_time = current_time
            last_validation_time = current_time
            
            # Determine which operations to perform
            do_polling = polling_interval is not None
            do_validation = validation_interval is not None
            
            while True:
                current_time = time.time()
                
                # RSS polling (if enabled)
                if do_polling and (current_time - last_polling_time) >= polling_interval/1000:
                    if not quiet:
                        print(f"Polling RSS feed")
                    
                    # Ensure session is fresh before polling
                    await self._ensure_fresh_session()
                    
                    try:
                        results = await poll_rss(self.ratelimiters['sec.gov'], self.session)
                        new_results = self._filter_new_accessions(results)
                        if new_results:
                            if not quiet:
                                print(f"Found {len(new_results)} new submissions via RSS")
                            if data_callback:
                                data_callback(new_results)
                    except Exception as e:
                        if not quiet:
                            print(f"RSS polling error: {e}, will recreate session on next poll")
                        # Force session recreation on next poll
                        if self.session:
                            await self.session.close()
                            self.session = None
                    
                    last_polling_time = current_time
                
                # EFTS validation (if enabled)
                if do_validation and (current_time - last_validation_time) >= validation_interval/1000:
                    # Get submissions from the last 24 hours for validation
                    today_date = datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%d')
                    if not quiet:
                        print(f"Validating submissions from {today_date}")

                    hits = clean_efts_hits(await self._async_run_efts_query(
                        filing_date=(today_date, today_date),
                        quiet=quiet
                    ))
                    
                    new_hits = self._filter_new_accessions(hits)
                    if new_hits:
                        if not quiet:
                            print(f"Found {len(new_hits)} new submissions via EFTS validation")
                        if data_callback:
                            data_callback(new_hits)
                    last_validation_time = current_time
                
                # Interval callback
                if interval_callback:
                    interval_callback()

                # Calculate next wake-up time
                next_times = []
                if do_polling:
                    next_times.append(last_polling_time + (polling_interval / 1000))
                if do_validation:
                    next_times.append(last_validation_time + (validation_interval / 1000))
                
                next_wake_time = min(next_times)
                current_time = time.time()
                time_to_sleep = max(0, next_wake_time - current_time)
                await asyncio.sleep(time_to_sleep)
                
        finally:
            # Clean up the session when done
            if self.session:
                await self.session.close()
                self.session = None

    def monitor_submissions(self, data_callback=None, interval_callback=None,
                            polling_interval=1000, quiet=True, start_date=None,
                            validation_interval=60000):
        """
        Monitor SEC submissions using the EDGAR system.
        :param data_callback: function to call with the data
        :param interval_callback: function that executes between polls
        :param polling_interval: interval between polls in milliseconds
        :param quiet: if True, suppresses output
        :param start_date: backfill start date in YYYY-MM-DD format
        :param validation_interval: interval between validation in milliseconds

        This function combines the speed of the RSS feed (fast, but misses some submissions) with the accuracy of the EFTS system.
        """
        # This is now a synchronous wrapper around the async implementation
        return asyncio.run(self._async_monitor_submissions(
            data_callback=data_callback,
            interval_callback=interval_callback,
            polling_interval=polling_interval,
            quiet=quiet,
            start_date=start_date,
            validation_interval=validation_interval
        ))
    
    def _filter_new_accessions(self, items):
        """Filter items to only include those with new accession numbers."""
        new_items = []
        for item in items:
            accession = item['accession']
            if accession not in self.accessions_set:  # O(1) lookup instead of O(n)
                # Check if deque is at capacity and will evict an item
                if len(self.accessions) == self.accessions.maxlen:
                    evicted_accession = self.accessions[0]  # Get leftmost item that will be evicted
                    self.accessions_set.discard(evicted_accession)  # Remove from set
                
                # Add to both structures
                self.accessions.append(accession)
                self.accessions_set.add(accession)
                new_items.append(item)
        return new_items
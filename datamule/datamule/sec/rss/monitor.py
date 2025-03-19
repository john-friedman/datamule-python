import asyncio
import aiohttp
from lxml import etree as ET
import time
from collections import deque
import pytz
from datetime import datetime
import re
from ..utils import PreciseRateLimiter, RateMonitor, RetryException, headers

class Monitor:
    def __init__(self):
        self.recent_accession_numbers = deque(maxlen=10000)  # Limit to recent 10,000 accessions
        self.limiter = None  # Will be initialized in monitor method
        self.rate_monitor = RateMonitor()  # Track request rates
        self.ns = {'atom': 'http://www.w3.org/2005/Atom'}  # XML namespace for Atom feed
        
    def _extract_cik(self, link_href):
        """Extract CIK from a link href URL"""
        # Format: https://www.sec.gov/Archives/edgar/data/351786/000110465925024964/0001104659-25-024964-index.htm
        match = re.search(r'/edgar/data/(\d+)/', link_href)
        if match:
            return match.group(1)
        return None
    
    def _extract_accession_number(self, id_text):
        """Extract accession number from id field"""
        # Format: urn:tag:sec.gov,2008:accession-number=0001104659-25-024964
        match = re.search(r'accession-number=([^&]+)', id_text)
        if match:
            return match.group(1)
        return None
    
    def _parse_entries(self, xml_content):
        """Parse XML content and extract relevant information from entries"""
        try:
            # Parse the XML content with lxml
            if isinstance(xml_content, bytes):
                parser = ET.XMLParser(recover=True)  # More forgiving parser
                root = ET.fromstring(xml_content, parser)
            else:
                parser = ET.XMLParser(recover=True)
                root = ET.fromstring(xml_content.encode('utf-8'), parser)
            
            # Get all entries
            entries = root.xpath('.//atom:entry', namespaces=self.ns)
            
            # Extract and group entries by accession number
            grouped_entries = {}
            
            for entry in entries:
                # Extract accession number
                id_element = entry.xpath('./atom:id', namespaces=self.ns)
                if not id_element or not id_element[0].text:
                    continue
                
                accession_number = self._extract_accession_number(id_element[0].text)
                if not accession_number:
                    continue
                
                # Extract link to get CIK
                link_element = entry.xpath('./atom:link[@rel="alternate"]', namespaces=self.ns)
                if not link_element or 'href' not in link_element[0].attrib:
                    continue
                
                cik = self._extract_cik(link_element[0].attrib['href'])
                if not cik:
                    continue
                
                # Extract submission type
                category_element = entry.xpath('./atom:category', namespaces=self.ns)
                if not category_element or 'term' not in category_element[0].attrib:
                    continue
                
                submission_type = category_element[0].attrib['term']
                if not submission_type:
                    continue
                
                # Add to grouped entries
                if accession_number not in grouped_entries:
                    grouped_entries[accession_number] = {
                        'accession_number': accession_number,
                        'submission_type': submission_type,
                        'ciks': []
                    }
                
                # Add CIK if not already in the list
                if cik not in grouped_entries[accession_number]['ciks']:
                    grouped_entries[accession_number]['ciks'].append(cik)
            
            return list(grouped_entries.values())
        
        except ET.XMLSyntaxError as e:
            print(f"Error parsing XML: {str(e)}")
            return []
        except Exception as e:
            print(f"Error processing entries: {str(e)}")
            return []
    
    async def _fetch_rss(self, session, url):
        """Fetch RSS feed with rate limiting and monitoring."""
        async with self.limiter:
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    content = await response.read()
                    await self.rate_monitor.add_request(len(content))
                    return content
            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Rate limit exceeded
                    retry_after = int(e.headers.get('Retry-After', 601))
                    raise RetryException(url, retry_after)
                raise
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
                return None
    
    async def _poll(self, session, base_url, poll_interval, quiet, poll_callback, known_accessions_set=None):
        """Poll RSS feed for new entries."""
        # Construct the polling URL for the first page
        poll_url = f"{base_url}&start=0&count=100"
        
        if not quiet:
            print(f"Polling {poll_url}")
        
        need_pagination = False
        new_entries = []
        
        try:
            # Fetch the first page
            xml_content = await self._fetch_rss(session, poll_url)
            if xml_content is None:
                # No content fetched, will wait below
                pass
            else:
                # Parse entries from the first page
                entries = self._parse_entries(xml_content)
                if entries:
                    # Filter out entries we've already seen
                    has_new_entries = False
                    
                    for entry in entries:
                        accession_number = entry['accession_number']
                        
                        # Check if we should skip this accession number
                        # It's new only if it's not in our recent list AND not in known_accessions_set
                        if (accession_number not in self.recent_accession_numbers and 
                            (known_accessions_set is None or accession_number not in known_accessions_set)):
                            has_new_entries = True
                            new_entries.append(entry)
                            self.recent_accession_numbers.append(accession_number)
                    
                    if has_new_entries:
                        if not quiet:
                            print(f"Found {len(new_entries)} new entries")
                        
                        # Determine if we need pagination - if we found new entries in the first page
                        need_pagination = True
        
        except RetryException as e:
            print(f"Rate limit exceeded. Retrying after {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            print(f"Error in poll: {str(e)}")
        
        # Always execute polling callback if provided, regardless of whether we found entries
        start_wait = time.time()
        if poll_callback:
            try:
                await poll_callback()
            except Exception as e:
                print(f"Error in poll callback: {str(e)}")
        
        # If we found new entries, return them immediately
        if need_pagination:
            return need_pagination, base_url, new_entries
            
        # Otherwise, wait for the polling interval (minus any time the callback took)
        elapsed = (time.time() - start_wait) * 1000
        if elapsed < poll_interval:
            await asyncio.sleep((poll_interval - elapsed) / 1000)
        
        return False, None, []
    
    async def _fetch_pages_concurrently(self, session, base_url, quiet, first_page_entries, known_accessions_set=None):
        """Fetch multiple pages concurrently to get all new entries efficiently."""
        # Start from page 2 (start=100) since we already have the first page
        max_start = 2000  # Max start value allowed
        page_size = 100
        batch_size = 10  # Number of concurrent requests
        
        all_new_entries = first_page_entries.copy()
        
        # Calculate the number of batches
        num_batches = (max_start - page_size) // (page_size * batch_size) + 1
        
        for batch_idx in range(num_batches):
            # Calculate start positions for this batch
            start_positions = [
                (batch_idx * batch_size * page_size) + (i * page_size) + page_size
                for i in range(batch_size)
                if (batch_idx * batch_size * page_size) + (i * page_size) + page_size <= max_start
            ]
            
            if not quiet:
                print(f"Fetching batch with start positions: {start_positions}")
            
            # Create tasks for concurrent fetching
            tasks = [
                self._fetch_rss(
                    session, 
                    f"{base_url}&start={pos}&count={page_size}"
                )
                for pos in start_positions
            ]
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            batch_has_new = False
            
            for xml_content in results:
                if isinstance(xml_content, Exception):
                    if isinstance(xml_content, RetryException):
                        print(f"Rate limit exceeded. Retrying after {xml_content.retry_after} seconds.")
                        await asyncio.sleep(xml_content.retry_after)
                    else:
                        print(f"Error in batch: {str(xml_content)}")
                    continue
                
                if xml_content:
                    entries = self._parse_entries(xml_content)
                    
                    # Filter entries we haven't seen yet
                    page_new_entries = []
                    for entry in entries:
                        accession_number = entry['accession_number']
                        
                        # Check if we should skip this accession number
                        # It's new only if it's not in our recent list AND not in known_accessions_set
                        if (accession_number not in self.recent_accession_numbers and 
                            (known_accessions_set is None or accession_number not in known_accessions_set)):
                            batch_has_new = True
                            page_new_entries.append(entry)
                            self.recent_accession_numbers.append(accession_number)
                    
                    all_new_entries.extend(page_new_entries)
            
            # If no new entries in this batch, we can stop
            if not batch_has_new:
                break
        
        return all_new_entries
    
    async def _monitor(self, data_callback, poll_callback, submission_type=None, cik=None, 
                      poll_interval=200, requests_per_second=2.0, quiet=True, 
                      known_accession_numbers=None):
        """Main monitoring loop."""
        # Initialize rate limiter
        self.limiter = PreciseRateLimiter(requests_per_second)
        
        # Create a set of known accession numbers for one-time filtering
        # This is separate from self.recent_accession_numbers which is used for ongoing tracking
        known_accessions_set = set(known_accession_numbers) if known_accession_numbers else set()
        
        # Construct base URL
        base_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent"
        
        # Add submission type filter if provided
        if submission_type:
            if isinstance(submission_type, list):
                types = ','.join(submission_type)
            else:
                types = submission_type
            base_url += f"&type={types}"
        
        # Add CIK filter if provided
        if cik:
            if isinstance(cik, list):
                ciks = ','.join(str(c) for c in cik)
            else:
                ciks = str(cik)
            base_url += f"&CIK={ciks}"
        
        # Start monitoring loop
        async with aiohttp.ClientSession(headers=headers) as session:
            while True:
                try:
                    # Poll for new entries
                    need_pagination, base_url_result, first_page_entries = await self._poll(
                        session, base_url, poll_interval, quiet, poll_callback, known_accessions_set
                    )
                    
                    if not need_pagination:
                        continue
                    
                    # Process additional pages if needed
                    all_new_entries = first_page_entries
                    
                    if need_pagination and len(first_page_entries) > 0:
                        all_new_entries = await self._fetch_pages_concurrently(
                            session, base_url, quiet, first_page_entries, known_accessions_set
                        )
                    
                    # Call data callback with all new entries
                    if all_new_entries and data_callback:
                        await data_callback(all_new_entries)
                    
                    # After the first run, clear the known_accessions_set as it's only needed once
                    if known_accessions_set:
                        if not quiet:
                            print(f"Cleared {len(known_accessions_set)} known accession numbers after first check")
                        known_accessions_set.clear()
                
                except Exception as e:
                    print(f"Error in monitor: {str(e)}")
                    await asyncio.sleep(poll_interval / 1000)

async def start_monitor(data_callback=None, poll_callback=None, submission_type=None, cik=None, 
                      poll_interval=200, requests_per_second=2.0, quiet=True, 
                      known_accession_numbers=None):
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
        known_accession_numbers=known_accession_numbers
    )

def monitor(data_callback=None, poll_callback=None, submission_type=None, cik=None, 
           poll_interval=200, requests_per_second=2.0, quiet=True, known_accession_numbers=None):
    """
    Convenience function to start monitoring SEC filings from the RSS feed.
    
    Parameters:
        data_callback (callable): Async function to call when new filings are found.
                                 Will be called with a list of dicts containing
                                 'accession_number', 'submission_type', and 'ciks'.
        poll_callback (callable): Async function to call during polling wait periods.
        submission_type (str or list): Form type(s) to monitor (e.g., "8-K", "10-Q").
        cik (str or list): CIK(s) to monitor.
        poll_interval (int): Polling interval in milliseconds.
        requests_per_second (float): Maximum requests per second.
        quiet (bool): Suppress verbose output.
        known_accession_numbers (list): List of accession numbers to skip (already processed).
    """
    return asyncio.run(start_monitor(
        data_callback=data_callback,
        poll_callback=poll_callback,
        submission_type=submission_type,
        cik=cik,
        poll_interval=poll_interval,
        requests_per_second=requests_per_second,
        quiet=quiet,
        known_accession_numbers=known_accession_numbers
    ))
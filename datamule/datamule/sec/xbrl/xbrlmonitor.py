import asyncio
import aiohttp
import time
from collections import deque
from lxml import etree
from ..utils import PreciseRateLimiter, headers

class XBRLMonitor:
    """
    Monitor for SEC XBRL RSS feed.
    Polls https://www.sec.gov/Archives/edgar/xbrlrss.all.xml for new XBRL filings.
    """
    
    def __init__(self, requests_per_second=2.0):
        """Initialize the XBRL Monitor."""
        self.url = "https://www.sec.gov/Archives/edgar/xbrlrss.all.xml"
        self.seen_accessions = deque(maxlen=2000)  # Store up to 2000 accession numbers
        self.limiter = PreciseRateLimiter(requests_per_second)
        self.headers = headers
        self.running = False
    
    async def _fetch_rss(self, session):
        """Fetch the XBRL RSS feed from SEC."""
        async with self.limiter:
            try:
                async with session.get(self.url) as response:
                    response.raise_for_status()
                    return await response.text()
            except Exception as e:
                print(f"Error fetching RSS feed: {str(e)}")
                return None
    
    def _parse_rss(self, xml_content):
        """Parse the XBRL RSS feed XML content using lxml."""
        # Parse XML using lxml
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml_content.encode('utf-8'), parser)
        
        # Define namespaces
        namespaces = {
            'edgar': 'https://www.sec.gov/Archives/edgar'
        }
        
        entries = []
        for item in root.findall('.//item'):
            # Get basic information
            title = item.find('title').text if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            
            # Get EDGAR-specific information
            edgar_filing = item.find('.//edgar:xbrlFiling', namespaces)
            if edgar_filing is not None:
                cik = edgar_filing.find('./edgar:cikNumber', namespaces).text if edgar_filing.find('./edgar:cikNumber', namespaces) is not None else ""
                acc_number = edgar_filing.find('./edgar:accessionNumber', namespaces).text if edgar_filing.find('./edgar:accessionNumber', namespaces) is not None else ""
                form_type = edgar_filing.find('./edgar:formType', namespaces).text if edgar_filing.find('./edgar:formType', namespaces) is not None else ""
                
                # Keep accession number with dashes
                if acc_number:
                    entries.append({
                        'accession_number': acc_number,
                        'cik': cik,
                        'submission_type': form_type,
                        'link': link
                    })
        
        return entries
        
    
    async def _poll_once(self, data_callback=None, quiet=True):
        """Internal async implementation of poll_once."""
        if not quiet:
            print(f"Polling {self.url}")
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            xml_content = await self._fetch_rss(session)
            if not xml_content:
                return []
            
            all_entries = self._parse_rss(xml_content)
            new_entries = []
            
            # Filter out entries we've already seen
            for entry in all_entries:
                if entry['accession_number'] not in self.seen_accessions:
                    self.seen_accessions.appendleft(entry['accession_number'])
                    new_entries.append(entry)

            if new_entries and not quiet:
                print(f"Found {len(new_entries)} new XBRL filings")
            
            # Call the callback if provided and if we have new entries
            if new_entries and data_callback:
                await data_callback(new_entries)
            
            return new_entries
    
    def poll_once(self, data_callback=None, quiet=True):
        """
        Poll the XBRL RSS feed once and process new filings.
        Synchronous wrapper around async implementation.
        """
        return asyncio.run(self._poll_once(data_callback, quiet))
    
    async def _monitor(self, data_callback=None, poll_callback=None, polling_interval=600000, quiet=True):
        """Internal async implementation of monitor."""
        self.running = True
        while self.running:
            try:
                # Poll once for new filings
                await self._poll_once(data_callback, quiet)
                
                # Execute polling callback if provided
                start_wait = time.time()
                if poll_callback:
                    try:
                        await poll_callback()
                    except Exception as e:
                        print(f"Error in poll callback: {str(e)}")
                
                # Sleep for the remaining interval time
                elapsed = (time.time() - start_wait) * 1000
                if elapsed < polling_interval:
                    await asyncio.sleep((polling_interval - elapsed) / 1000)
                
            except Exception as e:
                print(f"Error in monitoring: {str(e)}")
                await asyncio.sleep(polling_interval / 1000)
    
    def monitor(self, data_callback=None, poll_callback=None, polling_interval=600000, quiet=True):
        """
        Continuously poll the XBRL RSS feed at the specified interval.
        Synchronous wrapper around async implementation.
        """
        return asyncio.run(self._monitor(
            data_callback=data_callback,
            poll_callback=poll_callback,
            polling_interval=polling_interval,
            quiet=quiet
        ))
    
    def stop(self):
        """Stop the continuous polling."""
        self.running = False
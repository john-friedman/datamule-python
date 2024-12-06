# Monitors SEC for update

# uses asyncio and aiohhtp to monitor SEC for updates
#using url https://efts.sec.gov/LATEST/search-index?forms=-0&startdt=2024-12-05&enddt=2024-12-05
# uses current date of Eastern Time Zone to get the latest filings for the day, should check for daylight savings time
# modifiable param of how many ms to check for updates, default is 1000ms, lower values is 100ms.

import asyncio
from downloader_utils import _fetch, _get_current_eastern_date



class Monitor:
    def __init__(self):
        self.last_total = 0
        
    async def _poll(self, base_url, session, interval,quiet=True):
        """
        Continuously poll API until new submissions are found
        Returns new data when changes are detected
        """
        last_date = None
        
        while True:
            if quiet:
                print(f'Polling {base_url}...')
            current_date = _get_current_eastern_date()
            date_str = current_date.strftime('%Y-%m-%d')
            
            # If date changed, reset last_total
            if last_date != date_str:
                self.last_total = 0  # Set to 0 instead of None for new day
                last_date = date_str
                
            poll_url = f"{base_url}&startdt={date_str}&enddt={date_str}"
            
            data = await _fetch(session, poll_url, fmt='json')
            current_total = data['hits']['total']['value']
            
            # Only return if we have new submissions
            if current_total > self.last_total:
                self.last_total = current_total
                return current_total, data
                
            self.last_total = current_total
            await asyncio.sleep(interval / 1000)
        
    async def _retrieve(self):
        """Get new submissions when changes detected"""
        raise NotImplementedError("Retrieve function not implemented")
        
    async def monitor(self, form=None, interval=1000):
        """Main monitoring function that coordinates polling and retrieval"""
        if interval < 100:
            raise ValueError("SEC rate limit is 10 requests per second, set interval to 100ms or higher")

        if form is None:
            form = ['-0']
        elif isinstance(form, str):
            form = [form]

        base_url = 'https://efts.sec.gov/LATEST/search-index?forms=' + ','.join(form)    
        
        
        raise NotImplementedError("Monitor function not implemented")
        
    async def stream(self):
        """Create stream of new submissions"""
        raise NotImplementedError("Stream function not implemented")
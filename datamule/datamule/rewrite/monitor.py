import asyncio
import aiohttp
from datetime import timedelta, datetime
import pytz

def _get_current_eastern_date():
    """Get current date in US Eastern timezone (automatically handles DST) """
    eastern = pytz.timezone('America/New_York')
    return datetime.now(eastern)

class Monitor:
    def __init__(self):
        self.last_total = 0
        self.last_date = _get_current_eastern_date() - timedelta(days=1)
        self.submissions = []
        self.max_hits = 10000

    async def _poll(self, base_url, session, poll_interval, quiet):
        """
        Continuously poll API until new submissions are found
        Returns total count, data, and the successful poll URL
        """
        
        while True:
            current_date = _get_current_eastern_date() - timedelta(days=1)
            date_str = current_date.strftime('%Y-%m-%d')
            
            if self.last_date != date_str:
                print(f"New date: {date_str}")
                self.last_total = 0
                self.submissions = []
                self.last_date = date_str
                
            poll_url = f"{base_url}&startdt={date_str}&enddt={date_str}"
            if not quiet:
                print(f"Polling {poll_url}")
            
            try:
                data = await _fetch(session, poll_url, fmt='json')
                current_total = data['hits']['total']['value']
                
                if current_total > self.last_total:
                    print(f"New submissions found: {current_total - self.last_total}")
                    self.last_total = current_total
                    return current_total, data, poll_url
                    
                self.last_total = current_total
                await asyncio.sleep(poll_interval / 1000)
                
            except Exception as e:
                print(f"Error polling {poll_url}: {str(e)}")
                await asyncio.sleep(poll_interval / 1000)  # Wait before retrying

    async def _retrieve(self, poll_url, initial_data, session, quiet):
        """
        Retrieve all submissions using pagination, starting with initial poll data
        """
        from_position = 100
        
        submissions = []
        while from_position < 9900:
            retrieve_url = f"{poll_url}&from={from_position}"
            if not quiet:
                print(f"Retrieving {retrieve_url}")
                
            try:
                data = await _fetch(session, retrieve_url, fmt='json')
                page_hits = data['hits']['hits']
                
                if not page_hits:  # No more results
                    break
                    
                if len(page_hits) < 100:  # Partial page means we're done
                    break
                    
                from_position += 100
                submissions.extend(data['hits']['hits'])
                
            except Exception as e:
                print(f"Error retrieving {retrieve_url}: {str(e)}")
                await asyncio.sleep(1)  # Wait before retrying
                
        self.last_total = len(submissions)
        return submissions

    async def _monitor(self, callback, form=None, poll_interval=1000, quiet=True):
        if poll_interval < 100:
            raise ValueError("SEC rate limit is 10 requests per second, set poll_interval to 100ms or higher")

        if form is None:
            form = ['-0']
        elif isinstance(form, str):
            form = [form]

        base_url = 'https://efts.sec.gov/LATEST/search-index?forms=' + ','.join(form)    
        
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    # Poll until we find new submissions
                    _, data, poll_url = await self._poll(base_url, session, poll_interval, quiet)
                    
                    # Retrieve all submissions for this update
                    submissions = await self._retrieve(poll_url, data, session, quiet)
                    
                    # Find new hits by comparing against existing hits
                    existing_ids = [sub['_id'] for sub in self.submissions]
                    new_submissions = [sub for sub in submissions if sub['_id'] not in existing_ids]
                    
                    if new_submissions:
                        # Update our tracking of seen hits
                        self.submissions.extend(new_submissions)
                        # Call the callback with new hits
                        if callback:
                            await callback(new_submissions)
                        
                except Exception as e:
                    print(f"Error in monitor: {e}")
                    await asyncio.sleep(poll_interval / 1000)
                
                await asyncio.sleep(poll_interval / 1000)

    def monitor(self, callback=None, form=None, poll_interval=1000, quiet=True):
        """
        Main monitoring function that coordinates polling and retrieval
        Args:
            callback: Async function to call with new hits
            form: Form type(s) to monitor, defaults to ['-0'] for all forms
            poll_interval: Polling poll_interval in milliseconds, minimum 100ms
            quiet: Whether to suppress status messages
        """
        asyncio.run(self._monitor(callback, form, poll_interval, quiet))
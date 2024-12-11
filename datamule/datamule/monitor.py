import asyncio
import aiohttp
from datetime import timedelta, datetime
import pytz
from collections import deque
import time
from .helper import headers, identifier_to_cik

def _get_current_eastern_date():
    """Get current date in US Eastern timezone (automatically handles DST) """
    eastern = pytz.timezone('America/New_York')
    return datetime.now(eastern)

class PreciseRateLimiter:
    def __init__(self, rate, interval=1.0):
        self.rate = rate  # requests per interval
        self.interval = interval  # in seconds
        self.token_time = self.interval / self.rate  # time per token
        self.last_time = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            wait_time = self.last_time + self.token_time - now
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self.last_time = time.time()
            return True

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

class RateMonitor:
    def __init__(self, window_size=1.0):
        self.window_size = window_size
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def add_request(self, size_bytes):
        async with self._lock:
            now = time.time()
            self.requests.append((now, size_bytes))
            while self.requests and self.requests[0][0] < now - self.window_size:
                self.requests.popleft()
    
    def get_current_rates(self):
        now = time.time()
        while self.requests and self.requests[0][0] < now - self.window_size:
            self.requests.popleft()
        
        if not self.requests:
            return 0, 0
        
        request_count = len(self.requests)
        byte_count = sum(size for _, size in self.requests)
        
        requests_per_second = request_count / self.window_size
        mb_per_second = (byte_count / 1024 / 1024) / self.window_size
        
        return round(requests_per_second, 1), round(mb_per_second, 2)

class Monitor:
    def __init__(self):
        self.last_total = 0
        self.last_date = _get_current_eastern_date()
        self.submissions = []
        self.max_hits = 10000
        self.limiter = PreciseRateLimiter(5)  # 5 requests per second
        self.rate_monitor = RateMonitor()
        self.headers = headers

    async def _fetch_json(self, session, url):
        """Fetch JSON with rate limiting and monitoring."""
        async with self.limiter:
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    content = await response.read()
                    await self.rate_monitor.add_request(len(content))
                    return await response.json()
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
                return None

    async def _poll(self, base_url, session, poll_interval, quiet):
        """Poll API until new submissions are found."""
        while True:
            current_date = _get_current_eastern_date()
            date_str = current_date.strftime('%Y-%m-%d')
            
            if self.last_date != current_date.strftime('%Y-%m-%d'):
                print(f"New date: {date_str}")
                self.last_total = 0
                self.submissions = []
                self.last_date = date_str
            
            poll_url = f"{base_url}&startdt={date_str}&enddt={date_str}"
            if not quiet:
                print(f"Polling {poll_url}")
            
            try:
                data = await self._fetch_json(session, poll_url)
                if data:
                    current_total = data['hits']['total']['value']
                    if current_total > self.last_total:
                        print(f"Found {current_total - self.last_total} new submissions")
                        self.last_total = current_total
                        return current_total, data, poll_url
                    self.last_total = current_total
            except Exception as e:
                print(f"Error in poll: {str(e)}")
            
            await asyncio.sleep(poll_interval / 1000)

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
        submissions = []
        
        for result in results:
            if isinstance(result, Exception):
                print(f"Error in batch: {str(result)}")
                continue
            if result and 'hits' in result:
                submissions.extend(result['hits']['hits'])
        
        return submissions

    async def _retrieve(self, poll_url, initial_data, session, quiet):
        """Retrieve all submissions using parallel batch processing."""
        batch_size = 10  # Number of concurrent requests
        page_size = 100  # Results per request
        max_position = min(self.max_hits, self.last_total)
        submissions = []
        
        # Process in batches of concurrent requests
        for batch_start in range(0, max_position, batch_size * page_size):
            from_positions = [
                pos for pos in range(
                    batch_start,
                    min(batch_start + batch_size * page_size, max_position),
                    page_size
                )
            ]
            
            if not quiet:
                print(f"Retrieving batch from positions: {from_positions}")
            
            batch_submissions = await self._retrieve_batch(
                session, poll_url, from_positions, quiet
            )
            
            if not batch_submissions:
                break
                
            submissions.extend(batch_submissions)
            
            # If we got fewer results than expected, we're done
            if len(batch_submissions) < len(from_positions) * page_size:
                break
        
        return submissions

    async def _monitor(self, callback, form=None, cik=None, ticker=None, poll_interval=1000, quiet=True):
        """Main monitoring loop with parallel processing."""
        if poll_interval < 100:
            raise ValueError("SEC rate limit is 10 requests per second, set poll_interval to 100ms or higher")

        # Handle form parameter
        if form is None:
            form = ['-0']
        elif isinstance(form, str):
            form = [form]
        
        # Handle CIK/ticker parameter
        cik_param = None
        if ticker is not None:
            cik_param = identifier_to_cik(ticker)
        elif cik is not None:
            cik_param = cik if isinstance(cik, list) else [cik]

        # Construct base URL
        base_url = 'https://efts.sec.gov/LATEST/search-index?forms=' + ','.join(form)
        
        # Add CIK parameter if specified
        if cik_param:
            cik_list = ','.join(str(c).zfill(10) for c in cik_param)
            base_url += f"&ciks={cik_list}"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            while True:
                try:
                    # Poll until we find new submissions
                    _, data, poll_url = await self._poll(base_url, session, poll_interval, quiet)
                    
                    # Retrieve all submissions in parallel
                    submissions = await self._retrieve(poll_url, data, session, quiet)
                    
                    # Find new submissions
                    existing_ids = {sub['_id'] for sub in self.submissions}
                    new_submissions = [
                        sub for sub in submissions 
                        if sub['_id'] not in existing_ids
                    ]
                    
                    if new_submissions:
                        self.submissions.extend(new_submissions)
                        if callback:
                            await callback(new_submissions)
                        
                        reqs_per_sec, mb_per_sec = self.rate_monitor.get_current_rates()
                        if not quiet:
                            print(f"Current rates: {reqs_per_sec} req/s, {mb_per_sec} MB/s")
                    
                except Exception as e:
                    print(f"Error in monitor: {str(e)}")
                    await asyncio.sleep(poll_interval / 1000)
                
                await asyncio.sleep(poll_interval / 1000)

    def monitor_submissions(self, callback=None, form=None, cik=None, ticker=None, poll_interval=1000, quiet=True):
        """Start the monitoring process."""
        asyncio.run(self._monitor(callback, form, cik, ticker, poll_interval, quiet))

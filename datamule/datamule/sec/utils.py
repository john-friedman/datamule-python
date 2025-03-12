import asyncio
import time
from collections import deque


class RetryException(Exception):
    def __init__(self, url, retry_after=601): # SEC Rate limit is typically 10 minutes.
        self.url = url
        self.retry_after = retry_after

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

headers = {'User-Agent': 'John Smith johnsmith@gmail.com'}
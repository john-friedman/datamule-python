import asyncio
import aiohttp
import time

class PreciseRateLimiter:
    def __init__(self, rate=10, interval=1.0):
        self.rate = rate
        self.interval = interval
        self.token_time = self.interval / self.rate
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

class XBRLRetriever:
    def __init__(self):
        self.base_url = "https://data.sec.gov/api/xbrl/frames"
        self.headers = {
            'User-Agent': 'Your Name yourname@email.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        }
        self.session = None
        self.limiter = PreciseRateLimiter(10)

    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None

    async def _fetch_json(self, url):
        await self.limiter.acquire()
        try:
            async with self.session.get(url) as response:
                if response.status == 429:
                    await asyncio.sleep(61)
                    return await self._fetch_json(url)
                elif response.status == 200:
                    return await response.json()
                else:
                    print(f"Error {response.status} for URL: {url}")
                    return None
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def _build_url(self, params):
        taxonomy = params.get('taxonomy')
        concept = params.get('concept')
        unit = params.get('unit')
        period = params.get('period')
        
        if not all([taxonomy, concept, unit, period]):
            raise ValueError("Missing required parameters")
            
        return f"{self.base_url}/{taxonomy}/{concept}/{unit}/{period}.json"

    async def _get_xbrl_data(self, params_list):
        tasks = []
        urls = {}
        
        for params in params_list:
            url = self._build_url(params)
            urls[url] = params
            tasks.append(self._fetch_json(url))
        
        results = await asyncio.gather(*tasks)
        
        return {url: result for url, result in zip(urls.keys(), results) if result is not None}

    def get_xbrl_frames(self, params_list):
        async def _download():
            async with self as downloader:
                return await self._get_xbrl_data(params_list)

        return asyncio.run(_download())
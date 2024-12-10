import asyncio
import aiohttp
import time
from collections import deque
from ..parser.sgml_parsing.sgml_parser_cy import parse_sgml_submission
from ..helper import headers

class Downloader:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(5)
        self.rate_limit_window = deque()
        self.session = None

    async def __aenter__(self):
        await self._init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close()

    async def _init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=headers)

    async def _close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def _rate_limit(self):
        current_time = time.time()
        while self.rate_limit_window and current_time - self.rate_limit_window[0] > 1:
            self.rate_limit_window.popleft()
        
        if len(self.rate_limit_window) >= 10:
            await asyncio.sleep(1)
        self.rate_limit_window.append(current_time)

    async def _fetch(self, url):
        if not self.session:
            raise RuntimeError("Session not initialized. Use async with Downloader() as downloader:")
        
        async with self.semaphore:
            await self._rate_limit()
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(f"HTTP {response.status}: {response.reason}")
                return await response.text()

    async def download_async(self, url, output_dir=None):
        try:
            content = await self._fetch(url)
            return parse_sgml_submission(content=content, output_dir=output_dir)
        except Exception as e:
            print(f"Error processing URL {url}: {str(e)}")
            raise

    @classmethod
    async def download_urls(cls, urls, output_dir=None):
        async with cls() as downloader:
            tasks = [downloader.download_async(url, output_dir) for url in urls]
            return await asyncio.gather(*tasks, return_exceptions=True)

    @classmethod
    def download(cls, urls, output_dir=None):
        if isinstance(urls, str):
            urls = [urls]
        return asyncio.run(cls.download_urls(urls, output_dir))
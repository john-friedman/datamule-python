import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import random
import os
from global_vars import headers

class Downloader:
    def __init__(self, rate_limit=10, headers=None):
        self.rate_limit = rate_limit
        self.limiter = AsyncLimiter(rate_limit, 1)  # rate_limit requests per second
        self.headers = headers or {}

    async def _download_url(self, session, url, output_dir):
        max_retries = 5
        base_delay = 5

        filename = url.split('/')[-1]
        filepath = os.path.join(output_dir, filename)

        for attempt in range(max_retries):
            try:
                async with self.limiter:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 429:  # Too Many Requests
                            raise aiohttp.ClientResponseError(response.request_info, response.history, status=429)
                        content = await response.read()

                with open(filepath, 'wb') as f:
                    f.write(content)
                
                print(f"Downloaded: {url}")
                return filepath

            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limited. Retrying {url} in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    print(f"Error downloading {url}: {str(e)}")
                    return None
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")
                return None

        print(f"Max retries reached for {url}")
        return None

    async def _download_urls(self, urls, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                task = asyncio.create_task(self._download_url(session, url, output_dir))
                tasks.append(task)

            results = await asyncio.gather(*tasks)

        successful_downloads = [result for result in results if result is not None]
        print(f"Successfully downloaded {len(successful_downloads)} out of {len(urls)} URLs")
        return successful_downloads

    def run_download_urls(self, urls, output_dir='data'):
        return asyncio.run(self._download_urls(urls, output_dir))


urls_to_download = [
    "https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm",
    "https://www.sec.gov/Archives/edgar/data/320193/000119312514383437/d783162d10k.htm"
]

downloader = Downloader(headers=headers)
downloader.run_download_urls(urls_to_download, output_dir='filings')
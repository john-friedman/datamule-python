import os
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp
import aiofiles

async def _fetch(self, s, url, fmt='raw'):
    """Core fetch with rate limiting and formats
    s: session, fmt: raw/json/text"""
    async with self.domain_limiters.get(urlparse(url).netloc, self.domain_limiters['default']):
        async with s.get(url, headers=self.headers) as r:
            if r.status != 200:
                raise ValueError(f'Error fetching {url}: {r.status}')
            return await (r.json() if fmt=='json' else r.text() if fmt=='text' else r.read())

async def _write(self, fp, data):
    """Save data to filepath with dir creation 
    fp: filepath, data: content to save"""
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    async with aiofiles.open(fp, 'wb') as f:
        await f.write(data if isinstance(data, bytes) else data.encode())


def _construct_api_url(self, base, params): 
    return f"{base}?{urlencode(params)}"
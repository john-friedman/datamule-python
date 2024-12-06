import os
from urllib.parse import urlparse
from aiolimiter import AsyncLimiter
import aiofiles
from datetime import datetime
import pytz
import contextlib

# add option to set this to env
default_domain_limiters = {
    'efts.sec.gov': AsyncLimiter(10, 1),  # 10 requests per second 
    'www.sec.gov': AsyncLimiter(10, 1),
    'default': None
}

default_headers = {'User-Agent': 'John Smith johnsmith@gmail.com'}

def _get_current_eastern_date():
    """Get current date in US Eastern timezone (automatically handles DST) """
    eastern = pytz.timezone('America/New_York')
    return datetime.now(eastern)

def get_limiter(url):
    domain = urlparse(url).netloc
    return default_domain_limiters.get(domain, default_domain_limiters['default'])

async def _fetch(session, url, fmt='raw'):
    limiter = get_limiter(url)
    async with limiter or contextlib.nullcontext():  # Will handle rate limiting
        async with session.get(url, headers=default_headers) as response:
            if response.status != 200:
                raise ValueError(f'Error fetching {url}: {response.status}')
            
            if fmt == 'json':
                return await response.json()
            elif fmt == 'text':
                return await response.text()
            return await response.read()

async def _write(filepath, data):
    """Save data to file, creating directories if needed"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if not isinstance(data, bytes):
        data = data.encode()

    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(data)

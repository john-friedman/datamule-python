import os
from urllib.parse import urlparse
import aiohttp
import aiofiles
from datetime import datetime
import pytz

default_domain_limiters = {'https://efts.sec.gov/':10,'https://www.sec.gov/':10,'default':None}

def _get_current_eastern_date():
    """Get current date in US Eastern timezone (automatically handles DST) """
    eastern = pytz.timezone('America/New_York')
    return datetime.now(eastern)

async def _fetch(session, url, fmt='raw'):
    async with session.get(url) as response:
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

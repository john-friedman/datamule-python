import asyncio
import aiohttp
import json
from tqdm import tqdm
from ..utils import PreciseRateLimiter, RateMonitor, headers

async def fetch_company_facts(session, cik, rate_limiter, rate_monitor, pbar):
    # Format CIK with leading zeros to 10 digits
    formatted_cik = f"CIK{str(cik).zfill(10)}"
    url = f"https://data.sec.gov/api/xbrl/companyfacts/{formatted_cik}.json"
    
    try:
        # Acquire rate limit token
        await rate_limiter.acquire()
        
        async with session.get(url, headers=headers) as response:
            content_length = int(response.headers.get('Content-Length', 0))
            await rate_monitor.add_request(content_length)
            
            # Log current rates
            req_rate, mb_rate = rate_monitor.get_current_rates()
            pbar.set_postfix({"req/s": req_rate, "MB/s": mb_rate})
            
            # Handle rate limiting
            if response.status == 429:
                retry_after = int(response.headers.get('Retry-After', 601))
                pbar.set_description(f"Rate limited, retry after {retry_after}s")
                await asyncio.sleep(retry_after)
                pbar.set_description(f"Fetching CIK {cik}")
                return await fetch_company_facts(session, cik, rate_limiter, rate_monitor, pbar)
            
            # Handle other errors
            if response.status != 200:
                pbar.update(1)
                return {"error": f"HTTP {response.status}", "cik": cik}
            
            data = await response.json()
            pbar.update(1)
            return data
    
    except Exception as e:
        pbar.update(1)
        return {"error": str(e), "cik": cik}

async def stream_companyfacts(cik=None, requests_per_second=5, callback=None):
    if cik is None:
        return {"error": "No CIK provided. Please specify a CIK."}
    
    # Handle both single CIK and list of CIKs
    if not isinstance(cik, list):
        cik_list = [cik]
    else:
        cik_list = cik
    
    # Initialize rate limiter and monitor
    rate_limiter = PreciseRateLimiter(rate=requests_per_second)
    rate_monitor = RateMonitor(window_size=10.0)
    
    # Create progress bar
    pbar = tqdm(total=len(cik_list), desc="Fetching company facts")
    
    results = []
    async with aiohttp.ClientSession() as session:
        # Create tasks for all CIKs
        tasks = [
            fetch_company_facts(session, cik_item, rate_limiter, rate_monitor, pbar)
            for cik_item in cik_list
        ]
        
        # Process tasks as they complete
        for completed_task in asyncio.as_completed(tasks):
            data = await completed_task
            
            # Call callback if provided
            if callback and not (data and 'error' in data):
                callback(data)
            
            results.append(data)
    
    pbar.close()
    
    # If single CIK was passed, return just that result
    if len(cik_list) == 1:
        return results[0]
    
    # Otherwise return all results
    return results

def stream_company_facts(cik=None, requests_per_second=5, callback=None):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        stream_companyfacts(cik=cik, requests_per_second=requests_per_second, callback=callback)
    )
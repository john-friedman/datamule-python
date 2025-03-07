import os
import asyncio
import aiohttp
import urllib.parse
import ssl
import json
import time
from tqdm import tqdm

class Query:
    def __init__(self, api_key=None):
        self.API_BASE_URL = "https://sec-library.jgfriedman99.workers.dev/"
        self._api_key = api_key
        self.total_cost = 0
        self.remaining_balance = None
        self.start_time = None

    @property
    def api_key(self):
        return getattr(self, '_api_key', None) or os.getenv('DATAMULE_API_KEY')

    @api_key.setter
    def api_key(self, value):
        if not value:
            raise ValueError("API key cannot be empty")
        self._api_key = value

    async def _fetch_page(self, session, submission_type=None, cik=None, filing_date=None, page=1):
        params = {
            'api_key': self.api_key,
            'page': page
        }
        
        # Handle submission_type parameter
        if submission_type:
            if isinstance(submission_type, list):
                params['submission_type'] = ','.join(str(x) for x in submission_type)
            else:
                params['submission_type'] = str(submission_type)
        
        # Handle CIK parameter
        if cik:
            if isinstance(cik, list):
                params['cik'] = ','.join(str(x) for x in cik)
            else:
                params['cik'] = str(cik)
        
        # Handle filing_date parameter
        if filing_date:
            if isinstance(filing_date, tuple):
                params['startdt'] = str(filing_date[0])
                params['enddt'] = str(filing_date[1])
            else:
                if isinstance(filing_date, list):
                    params['filing_date'] = ','.join(str(x) for x in filing_date)
                else:
                    params['filing_date'] = str(filing_date)

        url = f"{self.API_BASE_URL}?{urllib.parse.urlencode(params)}"
        
        async with session.get(url) as response:
            data = await response.json()
            if not data.get('success'):
                raise ValueError(f"API request failed: {data.get('error')}")
            
            # Track costs and balance
            charges = data['metadata']['billing']['charges']
            page_cost = charges['total']
            self.total_cost += page_cost
            self.remaining_balance = data['metadata']['billing']['remaining_balance']
            
            return data['data'], data['metadata']['pagination'], page_cost

    async def execute_query(self, submission_type=None, cik=None, filing_date=None):
        if self.api_key is None:
            raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")
        
        self.start_time = time.time()
        total_items = 0
        pages_processed = 0
        
        # Display query parameters
        query_desc = []
        if cik:
            query_desc.append(f"CIK={cik}")
        if submission_type:
            query_desc.append(f"Type={submission_type}")
        if filing_date:
            if isinstance(filing_date, tuple):
                query_desc.append(f"Date={filing_date[0]} to {filing_date[1]}")
            else:
                query_desc.append(f"Date={filing_date}")
        
        if query_desc:
            print(f"QUERY: {', '.join(query_desc)}")
        
        connector = aiohttp.TCPConnector(ssl=ssl.create_default_context())
        async with aiohttp.ClientSession(connector=connector) as session:
            # Initialize progress bar with a custom format to avoid extra colons
            pbar = tqdm(unit="page", bar_format="{desc}: {n_fmt} {unit} [{elapsed}<{remaining}, {rate_fmt}{postfix}]")
            pbar.set_description("Fetching data")
            
            current_page = 1
            has_more = True
            results = []
            
            while has_more:
                # Fetch page
                page_results, pagination, page_cost = await self._fetch_page(session, 
                                                                    submission_type=submission_type, 
                                                                    cik=cik, 
                                                                    filing_date=filing_date, 
                                                                    page=current_page)
                
                # Accumulate results
                results.extend(page_results)
                
                pages_processed += 1
                total_items += len(page_results)
                
                # Update progress bar with cleaner format
                pbar.set_description(f"Fetching data (page {current_page})")
                pbar.set_postfix_str(f"cost=${self.total_cost:.2f} | balance=${self.remaining_balance:.2f}")
                pbar.update(1)
                
                # Check if we need to fetch more pages
                has_more = pagination.get('hasMore', False)
                current_page += 1
                
                # For the first page, display record info using pbar.write instead of print
                if pages_processed == 1:
                    records_per_page = pagination.get('currentPageRecords', len(page_results))
                    total_records = pagination.get('totalRecords', None)
                    if total_records:
                        pbar.write(f"Retrieved {records_per_page} records (page 1) of {total_records} total - Fetching additional pages...")
                    else:
                        pbar.write(f"Retrieved {records_per_page} records (page 1) - Fetching additional pages...")
            
            pbar.close()
            
            # Final summary
            elapsed_time = time.time() - self.start_time
            print("\nQuery complete:")
            print(f"- Retrieved {total_items} filings across {pages_processed} pages")
            print(f"- Total cost: ${self.total_cost:.2f}")
            print(f"- Remaining balance: ${self.remaining_balance:.2f}")
            print(f"- Time: {elapsed_time:.1f} seconds")
            
            return results


def query(cik=None, submission_type=None, filing_date=None, api_key=None):
    """
    Query SEC filings data with optional filtering
    
    Parameters:
    - cik: Company CIK number(s), can be string, int, or list
    - submission_type: Filing type(s), can be string or list (e.g., '10-K', ['10-K', '10-Q'])
    - filing_date: Filing date(s), can be string, list, or tuple of (start_date, end_date)
    - api_key: Optional API key (can also use DATAMULE_API_KEY environment variable)
    
    Returns:
    - List of all matching submission data
    """
    # Create a Query instance for this request
    q = Query(api_key=api_key)
    # remove dash from filing_date
    if isinstance(filing_date, tuple):
        filing_date = (filing_date[0].replace('-', ''), filing_date[1].replace('-', ''))
    elif isinstance(filing_date, str):
        filing_date = filing_date.replace('-', '')
    elif isinstance(filing_date, list):
        filing_date = [x.replace('-', '') for x in filing_date]

    print(filing_date)
    # Run the query and return results
    return asyncio.run(q.execute_query(
        submission_type=submission_type,
        cik=cik,
        filing_date=filing_date
    ))
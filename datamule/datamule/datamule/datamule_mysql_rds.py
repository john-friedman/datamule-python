import os
import asyncio
import aiohttp
import json
import ssl
import time
from tqdm import tqdm
from ..providers.providers import MAIN_API_ENDPOINT
class DatamuleMySQL:
    def __init__(self, api_key=None):
        self.API_BASE_URL = MAIN_API_ENDPOINT
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

    async def _fetch_page(self, session, database, params, page=1, page_size=25000):
        # Construct the URL with database name
        url = f"{self.API_BASE_URL}{database}"
        
        # Build query parameters, copy needed to prevent changing original over multiple executions.
        query_params = params.copy()
        
        # Add pagination and auth
        query_params["page"] = page
        query_params["pageSize"] = page_size
        query_params["api_key"] = self.api_key
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with session.get(url, params=query_params, headers=headers) as response:
            data = await response.json()
            print(response.url)
            if not data.get('success'):
                raise ValueError(f"API request failed: {data.get('error')}")
            
            # Track costs and balance from billing metadata
            billing = data.get('metadata', {}).get('billing', {})
            page_cost = billing.get('total_charge', 0)
            self.total_cost += page_cost
            self.remaining_balance = billing.get('remaining_balance')
            
            # Get pagination info
            pagination = data.get('metadata', {}).get('pagination', {})
            
            result_data = data.get('data', [])
            # If data is a dict with a 'data' key, unwrap it
            if isinstance(result_data, dict) and 'data' in result_data:
                result_data = result_data['data']
            return result_data, pagination, page_cost

    async def execute_query(self, database,  **kwargs):
        if self.api_key is None:
            raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")
        
        # Extract pagination and display options
        page_size = kwargs.pop('page_size', 25000)
        quiet = kwargs.pop('quiet', False)
        
        # Process filters: tuples = range, lists = OR, single = exact
        params = {}
        for key, value in kwargs.items():
            # Skip None values entirely
            if value is None:
                continue

            elif isinstance(value,list):
                params[key] = ','.join([str(val) for val in value])
            elif isinstance(value,tuple):
                params[f"{key}_START"] = value[0]
                params[f"{key}_END"] = value[1]
            else:
                params[key] = value

        
        self.start_time = time.time()
        total_items = 0
        pages_processed = 0
        
  
        connector = aiohttp.TCPConnector(ssl=ssl.create_default_context())
        async with aiohttp.ClientSession(connector=connector) as session:
            # Initialize progress bar only if not quiet
            if not quiet:
                pbar = tqdm(unit="page", bar_format="{desc}: {n_fmt} {unit} [{elapsed}<{remaining}, {rate_fmt}{postfix}]")
                pbar.set_description("Fetching data")
            
            current_page = 1
            has_more = True
            results = []
            
            while has_more:
                # Fetch page
                page_results, pagination, page_cost = await self._fetch_page(
                    session,
                    database,
                    params,
                    page=current_page,
                    page_size=page_size
                )
                
                # Accumulate results
                results.extend(page_results)
                
                pages_processed += 1
                total_items += len(page_results)
                
                # Update progress bar only if not quiet
                if not quiet:
                    pbar.set_description(f"Fetching data (page {current_page})")
                    pbar.set_postfix_str(f"cost=${self.total_cost:.4f} | balance=${self.remaining_balance:.2f}")
                    pbar.update(1)
                
                # Check if we need to fetch more pages
                has_more = pagination.get('hasMore', False)
                current_page += 1
                
                # For the first page, display record info only if not quiet
                if pages_processed == 1 and not quiet:
                    records_per_page = pagination.get('currentPageRecords', len(page_results))
                    if records_per_page > 0:
                        pbar.write(f"Retrieved {records_per_page} records (page 1) - Fetching additional pages...")
                    else:
                        pbar.write("No records found matching criteria")
                        break
            
            if not quiet:
                pbar.close()
            
            # Final summary only if not quiet
            if not quiet:
                elapsed_time = time.time() - self.start_time
                print("\nQuery complete:")
                print(f"- Retrieved {total_items} records across {pages_processed} pages")
                print(f"- Total cost: ${self.total_cost:.4f}")
                print(f"- Remaining balance: ${self.remaining_balance:.2f}")
                print(f"- Time: {elapsed_time:.1f} seconds")
            
            return results


def query_mysql_rds(database, api_key=None, **kwargs):

    # Create a DatamuleMySQL instance for this request
    dm = DatamuleMySQL(api_key=api_key)
    
    # Run the paginated query and return results
    return asyncio.run(dm.execute_query(database=database, **kwargs))
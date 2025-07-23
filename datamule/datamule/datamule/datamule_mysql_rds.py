import os
import asyncio
import aiohttp
import json
import ssl
import time
from tqdm import tqdm

class DatamuleMySQL:
    def __init__(self, api_key=None):
        self.API_BASE_URL = "https://datamule-mysql-rds.jgfriedman99.workers.dev"
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

    async def _fetch_page(self, session, table, database, filters, page=1, page_size=25000):
        payload = {
            "table": table,
            "database": database,
            "filters": filters,
            "page": page,
            "pageSize": page_size
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with session.post(self.API_BASE_URL, json=payload, headers=headers) as response:
            data = await response.json()
            if not data.get('success'):
                raise ValueError(f"API request failed: {data.get('error')}")
            
            # Track costs and balance
            billing = data['metadata']['billing']
            page_cost = billing['total_charge']
            self.total_cost += page_cost
            self.remaining_balance = billing['remaining_balance']
            
            return data['data'], data['metadata']['pagination'], page_cost

    async def execute_query(self, table, **kwargs):
        if self.api_key is None:
            raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")
        
        # Extract pagination and display options
        page_size = kwargs.pop('page_size', 25000)
        quiet = kwargs.pop('quiet', False)
        
        # Determine database from table
        if table == 'simple_xbrl':
            database = 'xbrl_db'
        elif table == 'accession_cik':
            database = 'lookup_db'
        elif table == 'submission_details':
            database = 'lookup_db'
        else:
            raise ValueError(f"Unsupported table: {table}")
        
        # Process filters: tuples = range, lists = OR, single = exact
        filters = {}
        for key, value in kwargs.items():
            # Skip None values entirely
            if value is None:
                continue
                
            # Special logic for cik
            if key == 'cik':
                if isinstance(value, list):
                    value = [int(val) for val in value]
                else:
                    value = [int(value)]
                filters[key] = {"type": "or", "values": value}
            elif isinstance(value, tuple):
                filters[key] = {"type": "range", "values": list(value)}
            elif isinstance(value, list):
                filters[key] = {"type": "or", "values": value}
            else:
                filters[key] = {"type": "or", "values": [value]}
        
        self.start_time = time.time()
        total_items = 0
        pages_processed = 0
        
        # Display query parameters
        query_desc = [f"Table={table}"]
        for key, filter_obj in filters.items():
            if filter_obj["type"] == "range":
                query_desc.append(f"{key}={filter_obj['values'][0]} to {filter_obj['values'][1]}")
            elif len(filter_obj["values"]) == 1:
                query_desc.append(f"{key}={filter_obj['values'][0]}")
            else:
                query_desc.append(f"{key}={filter_obj['values']}")
        
        if not quiet:
            print(f"QUERY: {', '.join(query_desc)}")
        
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
                    table=table,
                    database=database,
                    filters=filters,
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


def query_mysql_rds(table, api_key=None, **kwargs):
    """
    Query MySQL RDS data from Datamule with optional filtering and automatic pagination
    
    Parameters:
    - table: Table name (e.g., 'simple_xbrl')
    - cik: Company CIK number(s), can be int, string, or list
    - Any other filter parameters as keyword arguments
    - page_size: Number of records per page (max 25000, default 25000)
    - quiet: Boolean, whether to suppress progress output and summary (default False)
    - api_key: Optional API key (can also use DATAMULE_API_KEY environment variable)
    
    Filter value types:
    - Single value: Exact match
    - List: OR condition (any of the values)
    - Tuple: Range condition (between first and second values)
    
    Returns:
    - List of dictionaries containing the requested data (ready for pandas DataFrame)
    """
    # For backwards compatibility, handle non-paginated single requests
    if kwargs.get('_single_page', False):
        # Remove the flag and use original synchronous implementation
        kwargs.pop('_single_page')
        return _query_mysql_rds_single(table, api_key, **kwargs)
    
    # Create a DatamuleMySQL instance for this request
    dm = DatamuleMySQL(api_key=api_key)
    
    # Run the paginated query and return results
    return asyncio.run(dm.execute_query(table=table, **kwargs))


def _query_mysql_rds_single(table, api_key=None, **kwargs):
    """Original synchronous implementation for single page requests"""
    import urllib.request
    import urllib.error
    
    endpoint_url = "https://datamule-mysql-rds.jgfriedman99.workers.dev"
    
    # Get API key from parameter or environment
    if api_key is None:
        api_key = os.getenv('DATAMULE_API_KEY')
    
    if not api_key:
        return {"error": "API key required. Pass api_key parameter or set DATAMULE_API_KEY environment variable"}

    # Process filters: tuples = range, lists = OR, single = exact
    filters = {}
    for key, value in kwargs.items():
        # Skip None values entirely
        if value is None:
            continue
            
        # special logic for cik
        if key == 'cik':
            if isinstance(value, list):
                value = [int(val) for val in value]
            else:
                value = [int(value)]
            filters[key] = {"type": "or", "values": value}
        elif isinstance(value, tuple):
            filters[key] = {"type": "range", "values": list(value)}
        elif isinstance(value, list):
            filters[key] = {"type": "or", "values": value}
        else:
            filters[key] = {"type": "or", "values": [value]}
    
    payload = {"filters": filters}
    # add table to payload
    payload['table'] = table

    if table == 'simple_xbrl':
        payload['database'] = 'xbrl_db'
    else:
        raise ValueError("table not found")

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        endpoint_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=6000) as response:
            result = json.loads(response.read().decode('utf-8'))
            # Return just the data for single page requests
            return result.get('data', []) if result.get('success') else result
    except urllib.error.HTTPError as e:
        # Print the error response body
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {error_body}")
        try:
            error_json = json.loads(error_body)
            print(f"Error details: {error_json}")
        except json.JSONDecodeError:
            print(f"Raw error response: {error_body}")
        raise
import os
import asyncio
import aiohttp
import urllib.parse
import ssl
import time
from tqdm import tqdm

class DatamuleLookup:
    def __init__(self, api_key=None):
        self.API_BASE_URL = "https://datamule-lookup.jgfriedman99.workers.dev/"
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

    async def _fetch_page(self, session, cik=None, accession_number=None, submission_type=None, 
                         filing_date=None, columns=None, distinct=False, page=1, page_size=25000):
        params = {
            'api_key': self.api_key,
            'page': page,
            'pageSize': page_size
        }
        
        # Handle CIK parameter
        if cik:
            if isinstance(cik, list):
                params['cik'] = ','.join(str(x) for x in cik)
            else:
                params['cik'] = str(cik)
        
        # Handle accession number parameter
        if accession_number:
            if isinstance(accession_number, list):
                params['accessionNumber'] = ','.join(str(x) for x in accession_number)
            else:
                params['accessionNumber'] = str(accession_number)
        
        # Handle submission_type parameter
        if submission_type:
            if isinstance(submission_type, list):
                params['submissionType'] = ','.join(str(x) for x in submission_type)
            else:
                params['submissionType'] = str(submission_type)
        
        # Handle filing_date parameter
        if filing_date:
            if isinstance(filing_date, tuple):
                params['startDate'] = str(filing_date[0])
                params['endDate'] = str(filing_date[1])
            else:
                if isinstance(filing_date, list):
                    params['filingDate'] = ','.join(str(x) for x in filing_date)
                else:
                    params['filingDate'] = str(filing_date)
        
        # Handle columns parameter
        if columns:
            if isinstance(columns, list):
                params['columns'] = ','.join(columns)
            else:
                params['columns'] = str(columns)
        
        # Handle distinct parameter
        if distinct:
            params['distinct'] = 'true'

        url = f"{self.API_BASE_URL}?{urllib.parse.urlencode(params)}"
        
        async with session.get(url) as response:
            data = await response.json()
            if not data.get('success'):
                raise ValueError(f"API request failed: {data.get('error')}")
            
            # Track costs and balance
            billing = data['metadata']['billing']
            page_cost = billing['total_charge']
            self.total_cost += page_cost
            self.remaining_balance = billing['remaining_balance']
            
            return data['data'], data['metadata']['pagination'], page_cost

    async def execute_query(self, cik=None, accession_number=None, submission_type=None, 
                          filing_date=None, columns=None, distinct=False, page_size=25000, quiet=False):
        if self.api_key is None:
            raise ValueError("No API key found. Please set DATAMULE_API_KEY environment variable or provide api_key in constructor")
        
        self.start_time = time.time()
        total_items = 0
        pages_processed = 0
        
        # Display query parameters
        query_desc = []
        if cik:
            query_desc.append(f"CIK={cik}")
        if accession_number:
            query_desc.append(f"Accession={accession_number}")
        if submission_type:
            query_desc.append(f"Type={submission_type}")
        if filing_date:
            if isinstance(filing_date, tuple):
                query_desc.append(f"Date={filing_date[0]} to {filing_date[1]}")
            else:
                query_desc.append(f"Date={filing_date}")
        if columns:
            query_desc.append(f"Columns={columns}")
        if distinct:
            query_desc.append("DISTINCT=True")
        
        if query_desc and not quiet:
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
                    cik=cik,
                    accession_number=accession_number,
                    submission_type=submission_type, 
                    filing_date=filing_date,
                    columns=columns,
                    distinct=distinct,
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


def datamule_lookup(cik=None, accession_number=None, submission_type=None, filing_date=None, 
                   columns=None, distinct=False, page_size=25000, quiet=False, api_key=None):
    """
    Query SEC filing data from Datamule with optional filtering
    
    Parameters:
    - cik: Company CIK number(s), can be string, int, or list
    - accession_number: Accession number(s), can be string or list
    - submission_type: Filing type(s), can be string or list (e.g., '10-K', ['10-K', '10-Q'])
    - filing_date: Filing date(s), can be string, list, or tuple of (start_date, end_date)
    - columns: Column(s) to return, can be string or list. Options: 'accessionNumber', 'cik', 'filingDate', 'submissionType'
    - distinct: Boolean, whether to return distinct results only
    - page_size: Number of records per page (max 25000)
    - quiet: Boolean, whether to suppress progress output and summary
    - api_key: Optional API key (can also use DATAMULE_API_KEY environment variable)
    
    Returns:
    - List of dictionaries containing the requested data (ready for pandas DataFrame)
    """
    # Create a DatamuleLookup instance for this request
    dl = DatamuleLookup(api_key=api_key)
    
    # Format dates by removing dashes if present
    if isinstance(filing_date, tuple):
        filing_date = (filing_date[0].replace('-', ''), filing_date[1].replace('-', ''))
    elif isinstance(filing_date, str):
        filing_date = filing_date.replace('-', '')
    elif isinstance(filing_date, list):
        filing_date = [x.replace('-', '') for x in filing_date]
    
    # Set default columns if none specified
    if columns is None:
        columns = ['accessionNumber', 'cik', 'filingDate', 'submissionType','detectedTime']
    
    # Validate page_size
    page_size = min(max(1, page_size), 25000)
    
    # Run the query and return results
    return asyncio.run(dl.execute_query(
        cik=cik,
        accession_number=accession_number,
        submission_type=submission_type,
        filing_date=filing_date,
        columns=columns,
        distinct=distinct,
        page_size=page_size,
        quiet=quiet
    ))
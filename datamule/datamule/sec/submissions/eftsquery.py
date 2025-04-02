import asyncio
import aiohttp
from datetime import datetime
from urllib.parse import urlencode
from tqdm import tqdm
from ..utils import RetryException, PreciseRateLimiter, RateMonitor, headers

class EFTSQuery:
    def __init__(self, requests_per_second=5.0, quiet=False):
        self.base_url = "https://efts.sec.gov/LATEST/search-index"
        self.headers = headers
        self.limiter = PreciseRateLimiter(requests_per_second)
        self.rate_monitor = RateMonitor()
        self.session = None
        self.pbar = None
        self.quiet = quiet
        self.max_page_size = 100  # EFTS API limit
        self.fetch_queue = asyncio.Queue()
        self.connection_semaphore = asyncio.Semaphore(5)  # Max 5 concurrent connections
        self.max_efts_hits = 10000  # EFTS API hard limit
        self.total_results_to_fetch = 0
        self.pending_page_requests = []  # Store pages to fetch during planning phase
        self.initial_query_hit_count = 0  # Track initial query hits to avoid double counting
        self.was_primary_docs_query = False  # Track if original query was for primary docs
        self.true_total_docs = 0  # Track the true total number of documents
        self.processed_doc_count = 0  # Track how many documents we've processed
        self.original_forms = []  # Track original form request before adding exclusions
        
    def update_progress_description(self):
        if self.pbar:
            reqs_per_sec, mb_per_sec = self.rate_monitor.get_current_rates()
            self.pbar.set_description(
                f"Querying documents [Rate: {reqs_per_sec}/s | {mb_per_sec} MB/s]"
            )

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None

    async def search_name(self, name):
        """
        Search for companies by name using the EFTS name search endpoint.
        
        Parameters:
        name (str): Company name to search for
        
        Returns:
        list: List of dictionaries containing company information (entity, id, tickers if available)
        """
        if not self.session:
            raise RuntimeError("No active session. This method must be called within an async context.")
            
        url = f"{self.base_url}?keysTyped={name}"
        
        if not self.quiet:
            print(f"Searching for company: {name}")
            
        async with self.limiter:
            try:
                async with self.session.get(url) as response:
                    if response.status == 429:
                        raise RetryException(url)
                    response.raise_for_status()
                    content = await response.read()
                    await self.rate_monitor.add_request(len(content))
                    data = await response.json()
                    
                    if 'hits' in data and 'hits' in data['hits']:
                        hits = data['hits']['hits']
                        results = []
                        
                        for hit in hits:
                            source = hit.get('_source', {})
                            result = {
                                'entity': source.get('entity', ''),
                                'id': hit.get('_id', ''),
                                'tickers': source.get('tickers', '')
                            }
                            results.append(result)
                        
                        if not self.quiet and results:
                            # Create a compact display of results
                            display_results = [f"{r['entity']} [{r['id']}]" for r in results]
                            print(f"Name matches: {', '.join(display_results[:5])}")
                            if len(results) > 5:
                                print(f"...and {len(results) - 5} more matches")
                        
                        return results
                    return []
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    raise RetryException(url)
                if not self.quiet:
                    print(f"Error searching for company: {str(e)}")
                return []
            except Exception as e:
                if not self.quiet:
                    print(f"Error searching for company: {str(e)}")
                return []

    def _get_form_exclusions(self, form):
        """Dynamically generate form exclusions based on patterns"""
        # Skip already negated forms
        if form.startswith('-'):
            return []
            
        # For forms without "/A", exclude the amendment version
        if not form.endswith('/A'):
            return [f"-{form}/A"]
            
        # No exclusions for amendment forms
        return []

    def _prepare_params(self, cik=None, submission_type=None, filing_date=None, location=None):
        params = {}
        
        # Handle CIK
        if cik:
            if isinstance(cik, list):
                params['ciks'] = ','.join(str(int(c)).zfill(10) for c in cik)
            else:
                params['ciks'] = str(int(cik)).zfill(10)

        # Handle submission type with exact form matching
        if submission_type:
            # Store original form request for reference
            if isinstance(submission_type, list):
                self.original_forms = submission_type.copy()
                form_list = submission_type.copy()  # Create a copy to modify
            else:
                self.original_forms = [submission_type]
                form_list = [submission_type]  # Create a list to modify
            
            # Apply form exclusions for exact matching
            expanded_forms = []
            for form in form_list:
                # Add the original form
                expanded_forms.append(form)
                
                # Get and add any exclusions for this form
                exclusions = self._get_form_exclusions(form)
                expanded_forms.extend(exclusions)
            
            params['forms'] = ','.join(expanded_forms)
        else:
            # Default to primary documents only
            self.original_forms = ["-0"]
            params['forms'] = "-0"

        # Handle filing date
        if filing_date:
            if isinstance(filing_date, tuple):
                start_date, end_date = filing_date
                params['startdt'] = start_date
                params['enddt'] = end_date
            elif isinstance(filing_date, list):
                # Use the earliest and latest dates in the list
                dates = [d for d in filing_date if d]
                if dates:
                    params['startdt'] = min(dates)
                    params['enddt'] = max(dates)
            else:
                params['startdt'] = filing_date
                params['enddt'] = filing_date
        else:
            # Default to all available data
            params['startdt'] = "2001-01-01"
            params['enddt'] = datetime.now().strftime('%Y-%m-%d')
            
        # Handle location filtering
        if location:
            params['filter_location'] = location
            
        return params

    def _get_query_description(self, params):
        parts = []
        
        if 'ciks' in params:
            parts.append(f"cik={params['ciks']}")
        
        if 'forms' in params:
            parts.append(f"forms={params['forms']}")
            
        if 'startdt' in params and 'enddt' in params:
            parts.append(f"dates={params['startdt']} to {params['enddt']}")
            
        if 'filter_location' in params:
            parts.append(f"location={params['filter_location']}")
            
        return ", ".join(parts)

    async def _fetch_json(self, url):
        if not self.quiet:
            print(f"Fetching {url}...")
        async with self.connection_semaphore:
            async with self.limiter:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 429:
                            raise RetryException(url)
                        response.raise_for_status()
                        content = await response.read()
                        await self.rate_monitor.add_request(len(content))
                        self.update_progress_description()
                        return await response.json()
                except aiohttp.ClientResponseError as e:
                    if e.status == 429:
                        raise RetryException(url)
                    raise

    async def _fetch_worker(self):
        while True:
            try:
                params, from_val, size_val, callback = await self.fetch_queue.get()
                
                url = f"{self.base_url}?{urlencode(params, doseq=True)}&from={from_val}&size={size_val}"
                
                try:
                    data = await self._fetch_json(url)
                    if 'hits' in data:
                        hits = data['hits']['hits']
                        if self.pbar:
                            self.pbar.update(len(hits))
                        if callback:
                            await callback(hits)
                    self.fetch_queue.task_done()
                except RetryException as e:
                    if not self.quiet:
                        print(f"\nRate limited. Sleeping for {e.retry_after} seconds...")
                    await asyncio.sleep(e.retry_after)
                    # Put back in queue
                    await self.fetch_queue.put((params, from_val, size_val, callback))
                    self.fetch_queue.task_done()
                except Exception as e:
                    if not self.quiet:
                        print(f"\nError fetching {url}: {str(e)}")
                    self.fetch_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                if not self.quiet:
                    print(f"\nWorker error: {str(e)}")
                self.fetch_queue.task_done()

    def _split_date_range(self, start_date, end_date, num_splits=4):
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # For single day, just return it
        if start.date() == end.date():
            return [(start_date, end_date)]
            
        delta = (end - start) / num_splits
        
        date_ranges = []
        for i in range(num_splits):
            range_start = start + delta * i
            range_end = start + delta * (i + 1) if i < num_splits - 1 else end
            date_ranges.append((
                range_start.strftime('%Y-%m-%d'),
                range_end.strftime('%Y-%m-%d')
            ))
        
        return date_ranges

    def _get_form_groups(self, buckets, max_count, num_groups=5):
        total_docs = sum(b['doc_count'] for b in buckets)
        target_per_group = total_docs / num_groups
        
        buckets_sorted = sorted(buckets, key=lambda x: x['doc_count'], reverse=True)
        groups = []
        current_group = []
        current_count = 0
        
        for bucket in buckets_sorted:
            if current_count + bucket['doc_count'] > max_count and current_group:
                groups.append(current_group)
                current_group = [bucket['key']]
                current_count = bucket['doc_count']
            else:
                current_group.append(bucket['key'])
                current_count += bucket['doc_count']
                
        if current_group:
            groups.append(current_group)
            
        return groups

    def _preserve_form_exclusions(self, form_group):
        """Add necessary exclusions to a form group based on form patterns"""
        result = form_group.copy()
        
        # Check each form in the group to see if it needs exclusions
        for form in form_group:
            exclusions = self._get_form_exclusions(form)
            
            # Add exclusions if they're not already in the form group
            for excluded_form in exclusions:
                if excluded_form not in result:
                    result.append(excluded_form)
        
        return result

    def _store_page_request(self, params, total_hits, callback=None, is_initial_query=False):
        """Store pages to be requested later, after planning is complete"""
        page_size = self.max_page_size
        # Cap total_hits to what we can actually fetch (max 100 pages of 100 results)
        actual_hits = min(total_hits, self.max_efts_hits)
        
        # If this is the initial query, track hit count to avoid double counting
        if is_initial_query:
            self.initial_query_hit_count = actual_hits
        else:
            # Keep track of total processed documents
            self.processed_doc_count += actual_hits
            
        self.total_results_to_fetch += actual_hits
        
        num_pages = min((actual_hits + page_size - 1) // page_size, 100)  # Max 100 pages
        
        for page in range(num_pages):
            from_val = page * page_size
            self.pending_page_requests.append((params.copy(), from_val, page_size, callback))
            
    async def _test_query_size(self, params):
        """Get the total number of hits for a query"""
        url = f"{self.base_url}?{urlencode(params, doseq=True)}&from=0&size=1"
        data = await self._fetch_json(url)
        if not data or 'hits' not in data:
            return 0, None
        return data['hits']['total']['value'], data

    def _get_total_from_buckets(self, data):
        """Get the true total count from aggregation buckets"""
        if 'aggregations' in data and 'form_filter' in data['aggregations']:
            form_filter = data['aggregations']['form_filter']
            buckets = form_filter.get('buckets', [])
            other_count = form_filter.get('sum_other_doc_count', 0)
            
            # Calculate total from all buckets
            total = sum(bucket['doc_count'] for bucket in buckets) + other_count
            
            return total
        
        # Fallback to the reported hits total
        if 'hits' in data and 'total' in data['hits']:
            return data['hits']['total']['value']
            
        return 0

    async def _get_split_strategy(self, data):
        """Determine how to split a query that would return more than 10000 results"""
        if 'aggregations' in data and 'form_filter' in data['aggregations']:
            form_filter = data['aggregations']['form_filter']
            buckets = form_filter.get('buckets', [])
            other_count = form_filter.get('sum_other_doc_count', 0)
            
            # Check if we have form buckets and they're worth splitting on
            if len(buckets) > 0:
                # Try splitting by forms first
                form_groups = self._get_form_groups(buckets, 9000)
                if form_groups and len(form_groups) > 1:
                    # Track processed forms for later negation
                    processed_forms = [form for group in form_groups for form in group]
                    return {
                        'type': 'form', 
                        'form_groups': form_groups, 
                        'other_count': other_count, 
                        'buckets': buckets
                    }
        
        # Default to date splitting
        return {'type': 'date', 'splits': 4}

    def _get_negated_forms(self, buckets):
        """Generate a negated form list to capture all forms not in buckets"""
        negated_forms = [f"-{bucket['key']}" for bucket in buckets]
        return negated_forms

    async def _process_negated_forms_recursive(self, base_params, negated_forms, start_date, end_date, depth=0, callback=None):
        """Process queries for negated forms with recursive date splitting"""
        # Create params with negated forms
        params = base_params.copy()
        params['forms'] = ','.join(negated_forms)
        params['startdt'] = start_date
        params['enddt'] = end_date
        
        # Test query size
        total_hits, data = await self._test_query_size(params)
        
        # Skip if no results
        if total_hits == 0:
            if not self.quiet:
                print(f"Skipping negated forms query - no results returned")
            return
            
        if not self.quiet:
            query_desc = self._get_query_description(params)
            date_range = f"{start_date} to {end_date}"
            print(f"Planning: Analyzing negated forms query (depth {depth}): {date_range} [{total_hits:,} hits]")
        
        # If small enough or at max depth, process directly
        if total_hits < self.max_efts_hits or start_date == end_date:
            self._store_page_request(params, total_hits, callback)
            return
            
        # Split date range more aggressively (10 parts)
        date_ranges = self._split_date_range(start_date, end_date, 10)
        
        # Process each date range recursively
        for sub_start, sub_end in date_ranges:
            await self._process_negated_forms_recursive(
                base_params, negated_forms, sub_start, sub_end, depth + 1, callback
            )

    async def _process_query_recursive(self, params, processed_forms=None, depth=0, max_depth=3, callback=None, is_initial_query=True):
        """Process a query with recursive splitting until all chunks are under 10K"""
        if processed_forms is None:
            processed_forms = []
            
        total_hits, data = await self._test_query_size(params)
        
        if not self.quiet:
            query_desc = self._get_query_description(params)
            print(f"Planning: Analyzing {'  '*depth}query: {query_desc} [{total_hits:,} hits]")
        
        # If we're at the maximum recursion depth or hits are under limit, process directly
        if depth >= max_depth or total_hits < self.max_efts_hits:
            self._store_page_request(params, total_hits, callback, is_initial_query)
            return processed_forms
            
        # Need to split further
        split_strategy = await self._get_split_strategy(data)
        
        if split_strategy['type'] == 'form':
            # Split by form groups
            form_groups = split_strategy['form_groups']
            buckets = split_strategy['buckets']
            
            # Process form groups from buckets
            for group in form_groups:
                # Preserve necessary form exclusions when splitting form groups
                form_group = self._preserve_form_exclusions(group)
                form_params = params.copy()
                form_params['forms'] = ','.join(form_group)
                # Track which forms we've processed
                processed_forms.extend(group)
                await self._process_query_recursive(form_params, processed_forms, depth + 1, max_depth, callback, False)
                
            # Return processed forms to parent
            return processed_forms
        else:
            # Split by date ranges
            num_splits = split_strategy['splits']
            start_date = params['startdt']
            end_date = params['enddt']
            date_ranges = self._split_date_range(start_date, end_date, num_splits)
            
            for start, end in date_ranges:
                date_params = params.copy()
                date_params['startdt'] = start
                date_params['enddt'] = end
                await self._process_query_recursive(date_params, processed_forms, depth + 1, max_depth, callback, False)
                
            # Return processed forms to parent
            return processed_forms

    async def _start_query_phase(self, callback):
        """Start the query phase after planning is complete"""
        if not self.quiet:
            print("\n--- Starting query phase ---")
            self.pbar = tqdm(total=self.total_results_to_fetch, desc="Querying documents [Rate: 0/s | 0 MB/s]")
        
        # Queue all pending page requests
        for params, from_val, size_val, callback in self.pending_page_requests:
            await self.fetch_queue.put((params, from_val, size_val, callback))

    async def query(self, cik=None, submission_type=None, filing_date=None, location=None, callback=None, name=None):
        """
        Query SEC filings using the EFTS API.
        
        Parameters:
        cik (str or list): Central Index Key(s) for the company
        submission_type (str or list): Filing form type(s) to filter by
        filing_date (str, tuple, or list): Date or date range to filter by
        location (str): Location code to filter by (e.g., 'CA' for California)
        callback (function): Async callback function to process results as they arrive
        name (str): Company name to search for (alternative to providing CIK)
        
        Returns:
        list: List of filing documents matching the query criteria
        """
        # If both CIK and name are provided, raise an error
        if cik is not None and name is not None:
            raise ValueError("Please provide either 'name' or 'cik', not both")
            
        all_hits = []
        
        # Collector callback to gather all hits
        async def collect_hits(hits):
            all_hits.extend(hits)
            if callback:
                await callback(hits)
                
        async with self as client:
            # If name is provided, search for matching companies inside the context manager
            if name is not None:
                company_results = await self.search_name(name)
                if not company_results:
                    if not self.quiet:
                        print(f"No companies found matching: {name}")
                    return []
                    
                # Use the first (best) match's CIK
                cik = company_results[0]['id']
                if not self.quiet:
                    print(f"Using CIK {cik} for {company_results[0]['entity']}")
            
            # Now prepare parameters with the CIK (either provided directly or from name search)
            params = self._prepare_params(cik, submission_type, filing_date, location)
            
            # Check if this is a primary documents query
            self.was_primary_docs_query = '-0' in params.get('forms', '').split(',')
            
            # Reset state for new query
            self.total_results_to_fetch = 0
            self.pending_page_requests = []
            self.initial_query_hit_count = 0
            self.processed_doc_count = 0
            self.pbar = None
            
            # First check size
            if not self.quiet:
                print("\n--- Starting query planning phase ---")
                print("Analyzing request and splitting into manageable chunks...")
            
            total_hits, data = await self._test_query_size(params)
            
            if total_hits == 0:
                if not self.quiet:
                    print("No results found for this query.")
                return []
                
            # Get accurate total from aggregation buckets
            self.true_total_docs = self._get_total_from_buckets(data)
            if not self.quiet:
                print(f"Found {self.true_total_docs:,} total documents to retrieve.")
            
            # Start worker tasks
            workers = [asyncio.create_task(self._fetch_worker()) for _ in range(5)]
            
            # Process the query recursively, splitting as needed, and get processed forms
            processed_forms = await self._process_query_recursive(params, None, 0, 4, collect_hits, True)
            
            # Check if we need to process forms that weren't included in our form splitting
            # Only do this if:
            # 1. We split by form (processed_forms is not empty)
            # 2. We haven't processed all documents yet (processed_doc_count < true_total_docs)
            # 3. This was a forms=-0 query originally (for primary docs)
            
            if processed_forms and len(processed_forms) > 0 and self.processed_doc_count < self.true_total_docs:
                if self.was_primary_docs_query:
                    # We split a primary documents query, need to handle other document types
                    # Create a negated form query that also maintains primary docs constraint
                    negated_forms = [f"-{form}" for form in processed_forms]
                    negated_forms.append('-0')  # Keep primary documents constraint
                    
                    remaining_docs = self.true_total_docs - self.processed_doc_count
                    if not self.quiet:
                        print(f"Planning: Analyzing remaining primary document forms using negation (~{remaining_docs:,} hits)")
                    
                    # Process negated forms query with recursive date splitting
                    start_date = params['startdt']
                    end_date = params['enddt']
                    await self._process_negated_forms_recursive(
                        params, negated_forms, start_date, end_date, 0, collect_hits
                    )
                elif not self.quiet:
                    print("No additional forms to process with negation - not a primary documents query")
            elif not self.quiet:
                print("No additional forms to process with negation")
            
            # Start the download phase
            await self._start_query_phase(collect_hits)
            
            # Wait for all queued fetches to complete
            await self.fetch_queue.join()
            
            # Cancel worker tasks
            for worker in workers:
                worker.cancel()
            
            await asyncio.gather(*workers, return_exceptions=True)
            
            # Clean up
            if self.pbar:
                self.pbar.close()
                self.pbar = None
            
            if not self.quiet:
                print(f"\n--- Query complete: {len(all_hits):,} submissions retrieved ---")
            return all_hits

def query_efts(cik=None, submission_type=None, filing_date=None, location=None, requests_per_second=5.0, callback=None, quiet=False, name=None):
    """
    Convenience function to run a query without managing the async context.
    
    Parameters:
    cik (str or list): Central Index Key(s) for the company
    submission_type (str or list): Filing form type(s) to filter by
    filing_date (str, tuple, or list): Date or date range to filter by
    location (str): Location code to filter by (e.g., 'CA' for California)
    requests_per_second (float): Maximum requests per second to make to the SEC API
    callback (function): Async callback function to process results as they arrive
    quiet (bool): Whether to suppress progress output
    name (str): Company name to search for (alternative to providing CIK)
    
    Returns:
    list: List of filing documents matching the query criteria
    
    Example:
    To search by company name:
        results = query_efts(name="Tesla", submission_type="10-K")
        
    To search by CIK:
        results = query_efts(cik="1318605", submission_type="10-K")
    """
    async def run_query():
        query = EFTSQuery(requests_per_second=requests_per_second, quiet=quiet)
        return await query.query(cik, submission_type, filing_date, location, callback, name)
    
    return asyncio.run(run_query())
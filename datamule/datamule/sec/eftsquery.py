import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode
from tqdm import tqdm
from collections import deque

class RetryException(Exception):
    def __init__(self, url, retry_after=601): # SEC Rate limit is typically 10 minutes.
        self.url = url
        self.retry_after = retry_after

class PreciseRateLimiter:
    def __init__(self, rate, interval=1.0):
        self.rate = rate  # requests per interval
        self.interval = interval  # in seconds
        self.token_time = self.interval / self.rate  # time per token
        self.last_time = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            wait_time = self.last_time + self.token_time - now
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self.last_time = time.time()
            return True

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

class RateMonitor:
    def __init__(self, window_size=1.0):
        self.window_size = window_size
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def add_request(self, size_bytes):
        async with self._lock:
            now = time.time()
            self.requests.append((now, size_bytes))
            while self.requests and self.requests[0][0] < now - self.window_size:
                self.requests.popleft()
    
    def get_current_rates(self):
        now = time.time()
        while self.requests and self.requests[0][0] < now - self.window_size:
            self.requests.popleft()
        
        if not self.requests:
            return 0, 0
        
        request_count = len(self.requests)
        byte_count = sum(size for _, size in self.requests)
        
        requests_per_second = request_count / self.window_size
        mb_per_second = (byte_count / 1024 / 1024) / self.window_size
        
        return round(requests_per_second, 1), round(mb_per_second, 2)

class EFTSQuery:
    def __init__(self, requests_per_second=5.0):
        self.base_url = "https://efts.sec.gov/LATEST/search-index"
        self.headers = {'User-Agent': 'John Smith johnsmith@gmail.com'}
        self.limiter = PreciseRateLimiter(requests_per_second)
        self.rate_monitor = RateMonitor()
        self.session = None
        self.pbar = None
        self.max_page_size = 100  # SEC API limit
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

    def _prepare_params(self, cik=None, submission_type=None, filing_date=None):
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
            
        return params

    def _get_query_description(self, params):
        parts = []
        
        if 'ciks' in params:
            parts.append(f"cik={params['ciks']}")
        
        if 'forms' in params:
            parts.append(f"forms={params['forms']}")
            
        if 'startdt' in params and 'enddt' in params:
            parts.append(f"dates={params['startdt']} to {params['enddt']}")
            
        return ", ".join(parts)

    async def _fetch_json(self, url):
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
                    print(f"\nRate limited. Sleeping for {e.retry_after} seconds...")
                    await asyncio.sleep(e.retry_after)
                    # Put back in queue
                    await self.fetch_queue.put((params, from_val, size_val, callback))
                    self.fetch_queue.task_done()
                except Exception as e:
                    print(f"\nError fetching {url}: {str(e)}")
                    self.fetch_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
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
            print(f"Skipping negated forms query - no results returned")
            return
            
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
        print("\n--- Starting query phase ---")
        self.pbar = tqdm(total=self.total_results_to_fetch, desc="Querying documents [Rate: 0/s | 0 MB/s]")
        
        # Queue all pending page requests
        for params, from_val, size_val, callback in self.pending_page_requests:
            await self.fetch_queue.put((params, from_val, size_val, callback))

    async def query(self, cik=None, submission_type=None, filing_date=None, callback=None):
        params = self._prepare_params(cik, submission_type, filing_date)
        all_hits = []
        
        # Check if this is a primary documents query
        self.was_primary_docs_query = '-0' in params.get('forms', '').split(',')
        
        # Collector callback to gather all hits
        async def collect_hits(hits):
            all_hits.extend(hits)
            if callback:
                await callback(hits)
                
        async with self as client:
            # Reset state for new query
            self.total_results_to_fetch = 0
            self.pending_page_requests = []
            self.initial_query_hit_count = 0
            self.processed_doc_count = 0
            self.pbar = None
            
            # First check size
            print("\n--- Starting query planning phase ---")
            print("Analyzing request and splitting into manageable chunks...")
            
            total_hits, data = await self._test_query_size(params)
            
            if total_hits == 0:
                print("No results found for this query.")
                return []
                
            # Get accurate total from aggregation buckets
            self.true_total_docs = self._get_total_from_buckets(data)
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
                    print(f"Planning: Analyzing remaining primary document forms using negation (~{remaining_docs:,} hits)")
                    
                    # Process negated forms query with recursive date splitting
                    start_date = params['startdt']
                    end_date = params['enddt']
                    await self._process_negated_forms_recursive(
                        params, negated_forms, start_date, end_date, 0, collect_hits
                    )
                else:
                    print("No additional forms to process with negation - not a primary documents query")
            else:
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
            
            print(f"\n--- Query complete: {len(all_hits):,} submissions retrieved ---")
            return all_hits

def query_efts(cik=None, submission_type=None, filing_date=None, requests_per_second=5.0, callback=None):
    """
    Convenience function to run a query without managing the async context.
    """
    async def run_query():
        query = EFTSQuery(requests_per_second=requests_per_second)
        return await query.query(cik, submission_type, filing_date, callback)
    
    return asyncio.run(run_query())
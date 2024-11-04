import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import os
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode
import math
import re
import aiofiles
import json
import csv
from pkg_resources import resource_filename
import glob


from ..global_vars import headers, dataset_10q_url_list,dataset_10k_url_list
from ..helper import identifier_to_cik, load_package_csv, fix_filing_url
from .ftd import get_all_ftd_urls, process_all_ftd_zips
from .dropbox_downloader import DropboxDownloader
from .information_table_13f import download_and_process_13f_data
from ..sec_filing import Filing

class RetryException(Exception):
    def __init__(self, url, retry_after=601):
        self.url = url
        self.retry_after = retry_after

class Downloader:
    """
    A class for asynchronously downloading and managing SEC filing data.

    This class provides functionality to download various types of SEC filings,
    company metadata, and other SEC datasets. It handles rate limiting for SEC.gov
    domains and provides both synchronous and asynchronous interfaces.

    Attributes:
        headers (dict): HTTP headers used for requests, including User-Agent
        dataset_path (str): Default path for storing downloaded datasets
        domain_limiters (dict): Rate limiters for different SEC.gov domains

    Example:
        >>> downloader = Downloader()
        >>> downloader.set_headers("Your Name your@email.com")
        >>> downloader.download(form="10-K", ticker="AAPL", date="2023-01-01")
    """
    def __init__(self):
        self.headers = headers
        self.dataset_path = 'datasets'
        self.domain_limiters = {
            'www.sec.gov': AsyncLimiter(10, 1),
            'efts.sec.gov': AsyncLimiter(10, 1),
            'data.sec.gov': AsyncLimiter(10, 1),
            'default': AsyncLimiter(10, 1)
        }

    def set_limiter(self, domain, rate_limit):
        """
        Set a custom rate limit for a specific domain.

        Args:
            domain (str): The domain to set the rate limit for
            rate_limit (int): Number of requests allowed per second

        Example:
            >>> downloader.set_limiter('www.sec.gov', 5)
        """
        self.domain_limiters[domain] = AsyncLimiter(rate_limit, 1)

    def set_headers(self, user_agent):
        """
        Set custom headers for HTTP requests.

        Args:
            user_agent (str): User agent string for SEC.gov requests
                Should be in format "Name Email"

        Example:
            >>> downloader.set_headers("Your Name your@email.com")
        """
        self.headers = {'User-Agent': user_agent}


    def get_limiter(self, url):
        """Get the appropriate rate limiter for a given URL."""
        domain = urlparse(url).netloc
        return self.domain_limiters.get(domain, self.domain_limiters['default'])
    
    async def _fetch_content_from_url(self, session, url):
        limiter = self.get_limiter(url)
        async with limiter:
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 429:
                        raise RetryException(url)
                    
                    response.raise_for_status()
                    return await response.read()
            
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    raise RetryException(url)
                raise
            
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")
                raise

    async def write_content_to_file(self, content, filepath):
        """Write content to a file asynchronously."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(content)

    def generate_url(self, base_url, params):
        """
        Generate a complete URL by combining base URL with query parameters.

        Args:
            base_url (str): Base URL (e.g., 'https://efts.sec.gov/search')
            params (dict): Query parameters to append

        Returns:
            str: Complete URL with encoded parameters

        Example:
            >>> generate_url('https://api.sec.gov', {'form': '10-K'})
            'https://api.sec.gov?form=10-K'
        """
        return f"{base_url}?{urlencode(params)}"

    async def download_file(self, session, url, output_path):
        """Download a file from a URL and save it to the specified path."""
        content = await self._fetch_content_from_url(session, url)
        await self.write_content_to_file(content, output_path)
        return output_path

    async def _fetch_json_from_url(self, session, url):
        """Asynchronously fetch JSON data from a URL."""
        content = await self._fetch_content_from_url(session, url)
        return json.loads(content)

    async def _download_urls(self, urls, filenames, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            total_files = len(urls)
            completed_files = 0
            
            with tqdm(total=total_files, desc="Downloading files") as pbar:
                while urls and completed_files < total_files:
                    tasks = [asyncio.create_task(self.download_file(session, url, os.path.join(output_dir, filename))) 
                             for url, filename in zip(urls, filenames) if filename]
                    
                    rate_limited = False
                    retry_after = 0
                    
                    pending = tasks
                    while pending:
                        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                        
                        for task in done:
                            try:
                                result = await task
                                completed_files += 1
                                pbar.update(1)
                            except RetryException as e:
                                print(f"\nRate limited for {e.url}. Will retry after {e.retry_after} seconds.")
                                rate_limited = True
                                retry_after = max(retry_after, e.retry_after)
                                break
                            except Exception as e:
                                print(f"\nFailed to download: {str(e)}")
                                completed_files += 1
                                pbar.update(1)
                        
                        if rate_limited:
                            break
                    
                    if rate_limited:
                        for task in pending:
                            task.cancel()
                        
                        print(f"\nRate limit hit. Sleeping for {retry_after} seconds before retrying.")
                        await asyncio.sleep(retry_after)
                        
                        # Recreate the list of URLs and filenames that haven't been processed
                        urls = [task.get_coro().cr_frame.f_locals['url'] for task in pending]
                        filenames = [filename for url, filename in zip(urls, filenames) if url in urls]
                    else:
                        break  # All tasks completed successfully

            print(f"\nSuccessfully downloaded {completed_files} out of {total_files} URLs")
            return completed_files

    def run_download_urls(self, urls, filenames, output_dir='filings'):
        """Download a list of URLs to a specified directory"""
        return asyncio.run(self._download_urls(urls, filenames, output_dir))

    async def _get_filing_urls_from_efts(self, base_url, sics=None, items=None, file_types=None):
        """Asynchronously fetch all filing URLs from a given EFTS URL."""
        full_urls = []
        file_dates = []
        start, page_size = 0, 100
        async with aiohttp.ClientSession() as session:
            while True:
                tasks = [self._fetch_json_from_url(session, f"{base_url}&from={start + i * page_size}") for i in range(10)]
                results = await atqdm.gather(*tasks, desc="Fetching URLs")
                for data in results:
                    if data and 'hits' in data:
                        
                        hits = data['hits']['hits']
                        if not hits:
                            return full_urls
                        
                        for hit in hits:
                            # Check SIC filter
                            sic_match = sics is None or any(int(sic) in sics for sic in hit['_source'].get('sics', []))
                            
                            # Check item filter
                            item_match = items is None or any(item in items for item in hit['_source'].get('items', []))
                            
                            # Check file type filter
                            file_type_match = file_types is None or hit['_source'].get('file_type') in (file_types if isinstance(file_types, list) else [file_types])
                            
                            if sic_match and item_match and file_type_match:
                                url = f"https://www.sec.gov/Archives/edgar/data/{hit['_source']['ciks'][0]}/{hit['_id'].split(':')[0].replace('-', '')}/{hit['_id'].split(':')[1]}"
                                filing_date = hit['_source']['file_date']
                                full_urls.append(url)
                                file_dates.append(filing_date)
                        
                        if start + page_size > data['hits']['total']['value']:
                            return full_urls,file_dates
                start += 10 * page_size

        return full_urls,file_dates

    async def _number_of_efts_filings(self, session, url):
        """Get the number of filings from a given EFTS URL asynchronously."""
        limiter = self.get_limiter(url)
        async with limiter:
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 429:
                        raise RetryException(url)
                    response.raise_for_status()
                    data = await response.json()
                    return sum(bucket['doc_count'] for bucket in data['aggregations']['form_filter']['buckets'])
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    raise RetryException(url)
                raise
            except Exception as e:
                print(f"Error fetching number of filings from {url}: {str(e)}")
                raise

    def _subset_urls(self, full_url, total_filings, target_filings_per_range=1000):
        """Split an EFTS URL into multiple URLs based on the number of filings."""
        parsed_url = urlparse(full_url)
        params = parse_qs(parsed_url.query)
        start = datetime.strptime(params.get('startdt', [None])[0], "%Y-%m-%d")
        end = datetime.strptime(params.get('enddt', [None])[0], "%Y-%m-%d")

        if start == end:
            forms = params.get('forms', [None])[0]
            if forms == '-0':
                urls = []
                for form in ['SC 13G', 'SC 13G/A']:
                    new_params = params.copy()
                    new_params['forms'] = [form]
                    urls.append(parsed_url._replace(query=urlencode(new_params, doseq=True)).geturl())
                return urls
            else:
                return [full_url]

        num_ranges = math.ceil(total_filings / target_filings_per_range)
        days_per_range = math.ceil((end - start).days / num_ranges)
        
        urls = []
        current_start = start
        for _ in range(num_ranges):
            current_end = min(current_start + timedelta(days=days_per_range), end)
            new_params = params.copy()
            new_params['startdt'] = [current_start.strftime('%Y-%m-%d')]
            new_params['enddt'] = [current_end.strftime('%Y-%m-%d')]
            urls.append(parsed_url._replace(query=urlencode(new_params, doseq=True)).geturl())
            if current_end == end:
                break
            current_start = current_end + timedelta(days=1)

        return urls[::-1]

    async def _conductor(self, efts_url, return_urls, output_dir, sics, items, file_types):
        """Conduct the download process based on the number of filings."""
        async with aiohttp.ClientSession() as session:
            try:
                total_filings = await self._number_of_efts_filings(session, efts_url)
            except RetryException as e:
                print(f"Rate limited when fetching number of filings. Retrying after {e.retry_after} seconds.")
                await asyncio.sleep(e.retry_after)
                return await self._conductor(efts_url, return_urls, output_dir, sics, items, file_types)

        all_primary_doc_urls = []
        
        if total_filings < 10000:
            primary_doc_urls,file_dates = await self._get_filing_urls_from_efts(efts_url, sics=sics, items=items, file_types=file_types)
            primary_doc_urls = [fix_filing_url(url) for url in primary_doc_urls]
            print(f"{efts_url}\nTotal filings: {len(primary_doc_urls)}")
            
            if return_urls:
                return primary_doc_urls
            else:
                filenames = [f"{url.split('/')[7]}_{filing_date}.htm" for url,filing_date in zip(primary_doc_urls,file_dates)]
                await self._download_urls(urls=primary_doc_urls, filenames=filenames, output_dir=output_dir)
                return None
        
        for subset_url in self._subset_urls(efts_url, total_filings):
            sub_primary_doc_urls = await self._conductor(efts_url=subset_url, return_urls=True, output_dir=output_dir, sics=sics, items=items, file_types=file_types)
            
            if return_urls:
                all_primary_doc_urls.extend(sub_primary_doc_urls)
            else:
                filenames = [f"{url.split('/')[7]}_{url.split('/')[-1]}" for url in sub_primary_doc_urls]
                await self._download_urls(urls=sub_primary_doc_urls, filenames=filenames, output_dir=output_dir)
        
        return all_primary_doc_urls if return_urls else None

    def download(self, output_dir='filings', return_urls=False, cik=None, ticker=None, 
                form=None, date=None, sics=None, items=None, file_types=None):
        """
        Download SEC filings based on specified criteria and filters.

        This method queries the SEC EFTS API to download filings matching the provided criteria.
        It handles rate limiting, pagination, and supports various filtering options.

        Args:
            output_dir (str, optional): Directory where downloaded filings will be saved.
                Defaults to 'filings'.
            return_urls (bool, optional): If True, returns list of filing URLs instead of
                downloading them. Defaults to False.
            cik (str|list, optional): Central Index Key(s) of companies. Can be single CIK
                or list of CIKs. Will be zero-padded to 10 digits.
            ticker (str, optional): Stock ticker symbol. Will be converted to CIK.
                Mutually exclusive with cik parameter.
            form (str|list, optional): SEC form type(s) to download. Examples:
                - Single form: "10-K", "10-Q", "8-K"
                - Multiple forms: ["10-K", "10-Q"]
                - Defaults to "-0" (all forms)
            date (str|tuple|list, optional): Filing date criteria. Can be:
                - Single date: "2023-01-01"
                - Date range tuple: ("2023-01-01", "2023-12-31")
                - List of dates: ["2023-01-01", "2023-02-01"]
                - Defaults to all dates from 2001-01-01 to present
            sics (list, optional): Standard Industrial Classification codes to filter by.
                Example: [1311, 2834]
            items (list, optional): Form-specific item numbers to filter by.
                Example: ["1.01", "2.01"] for 8-K items
            file_types (str|list, optional): Types of files to download.
                Examples: "EX-10", ["EX-10", "EX-21"]

        Returns:
            list|None: If return_urls=True, returns list of filing URLs.
                Otherwise returns None.

        Raises:
            ValueError: If both cik and ticker are provided
            aiohttp.ClientError: For HTTP request failures
            RetryException: When SEC rate limit is hit

        Examples:
            Download Apple's 10-K filings from 2023:
            >>> downloader = Downloader()
            >>> downloader.download(
            ...     ticker="AAPL",
            ...     form="10-K",
            ...     date=("2023-01-01", "2023-12-31")
            ... )

            Get URLs for multiple companies' 8-Ks:
            >>> urls = downloader.download(
            ...     cik=["320193", "789019"],
            ...     form="8-K",
            ...     return_urls=True
            ... )

            Download specific exhibits for a date range:
            >>> downloader.download(
            ...     ticker="MSFT",
            ...     file_types=["EX-99.1"],
            ...     date=("2022-01-01", "2022-12-31")
            ... )

            Download filings for specific SIC codes:
            >>> downloader.download(
            ...     form="10-Q",
            ...     sics=[1311, 2834],  # Oil/Gas, Pharmaceutical
            ...     date="2023-01-01"
            ... )

        Notes:
            - The method handles SEC.gov rate limiting automatically
            - Large date ranges are automatically split into smaller chunks
            - Downloaded files are named as: {cik}_{filename}
            - Use return_urls=True to get URLs without downloading
        """
        base_url = "https://efts.sec.gov/LATEST/search-index"
        params = {}

        if sum(x is not None for x in [cik, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik or ticker')
        
        if ticker is not None:
            cik = identifier_to_cik(ticker)
                
        if cik:
            if isinstance(cik, list):
                formatted_ciks = ','.join(str(c).zfill(10) for c in cik)
            else:
                formatted_ciks = str(cik).zfill(10)
            params['ciks'] = formatted_ciks
        
        params['forms'] = ','.join(form) if isinstance(form, list) else form if form else "-0"
        
        if file_types:
            params['q'] = '-'
            if isinstance(file_types, list):
                params['file_type'] = ','.join(file_types)
            else:
                params['file_type'] = file_types
        
        if isinstance(date, list):
            efts_url_list = [self.generate_url(base_url, {**params, 'startdt': d, 'enddt': d}) for d in date]
        elif isinstance(date, tuple):
            efts_url_list = [self.generate_url(base_url, {**params, 'startdt': date[0], 'enddt': date[1]})]
        else:
            date_str = date if date else f"2001-01-01,{datetime.now().strftime('%Y-%m-%d')}"
            efts_url_list = [self.generate_url(base_url, {**params, 'startdt': date_str.split(',')[0], 'enddt': date_str.split(',')[1]})]
        
        all_primary_doc_urls = []
        for efts_url in efts_url_list:
            if return_urls:
                all_primary_doc_urls.extend(asyncio.run(self._conductor(efts_url=efts_url, return_urls=True, output_dir=output_dir, sics=sics, items=items, file_types=file_types)))
            else:
                asyncio.run(self._conductor(efts_url=efts_url, return_urls=False, output_dir=output_dir, sics=sics, items=items, file_types=file_types))
        
        return all_primary_doc_urls if return_urls else None

    def download_company_concepts(self, output_dir='company_concepts', cik=None, ticker=None):
        """
        Download XBRL company concepts and facts data from SEC's API.

        Retrieves company financial facts in structured XBRL format, including historical values
        for balance sheet, income statement, and other disclosure concepts.

        Args:
            output_dir (str, optional): Directory to save downloaded files.
                Defaults to 'company_concepts'.
            cik (str|list, optional): Central Index Key(s). Can be:
                - Single CIK: "320193" 
                - List of CIKs: ["320193", "789019"]
                - If neither cik nor ticker provided, downloads all companies
            ticker (str, optional): Stock ticker symbol. Will be converted to CIK.
                Mutually exclusive with cik parameter.

        Raises:
            ValueError: If both cik and ticker are provided

        Examples:
            Download Apple's XBRL facts:
            >>> downloader.download_company_concepts(ticker="AAPL")

            Download multiple specific companies:
            >>> downloader.download_company_concepts(
            ...     cik=["320193", "789019"]  # Apple and Microsoft
            ... )
        """
        if sum(x is not None for x in [cik, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik or ticker')
        
        ciks = None
        if cik:
            if isinstance(cik, list):
                ciks = cik
            else:
                ciks = [cik]
        
        if ticker is not None:
            ciks = identifier_to_cik(ticker)

        if ciks is None:
            company_tickers = load_package_csv('company_tickers')
            ciks = [company['cik'] for company in company_tickers]
            
        os.makedirs(output_dir, exist_ok=True)
                
        urls = [f'https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json' for cik in ciks]
        filenames = [f"CIK{str(cik).zfill(10)}.json" for cik in ciks]
        self.run_download_urls(urls=urls, filenames=filenames, output_dir=output_dir)


    def download_dataset(self, dataset, dataset_path='datasets'):
        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)

        if re.match(r"10k_(\d{4})$", dataset):
            dropbox_downloader = DropboxDownloader()
            year = int(dataset.split('_')[-1])
            year_data = next((data for data in dataset_10k_url_list if data['year'] == year), None)
            
            if year_data:
                output_dir = os.path.join(dataset_path, f'10K_{year}')
                os.makedirs(output_dir, exist_ok=True)
                
                dropbox_downloader.download(urls=year_data['urls'], output_dir=output_dir)
            else:
                print(f"No data found for 10Q_{year}")
        elif dataset == 'ftd':
            output_dir = os.path.join(dataset_path, 'ftd')
            urls = get_all_ftd_urls()
            self.run_download_urls(urls, filenames=[url.split('/')[-1] for url in urls], output_dir=output_dir)
            process_all_ftd_zips(output_dir)
        elif dataset == '13f_information_table':    
            output_dir = os.path.join(dataset_path, '13f_information_table')
            download_and_process_13f_data(self, output_dir)

        elif re.match(r"10q_(\d{4})$", dataset):
            dropbox_downloader = DropboxDownloader()
            year = int(dataset.split('_')[-1])
            year_data = next((data for data in dataset_10q_url_list if data['year'] == year), None)
            
            if year_data:
                output_dir = os.path.join(dataset_path, f'10Q_{year}')
                os.makedirs(output_dir, exist_ok=True)
                
                dropbox_downloader.download(urls=year_data['urls'], output_dir=output_dir)
            else:
                print(f"No data found for 10Q_{year}")

        elif re.match(r"10k_(\d{4})$", dataset):
            dropbox_downloader = DropboxDownloader()
            year = int(dataset.split('_')[-1])
            year_data = next((data for data in dataset_10k_url_list if data['year'] == year), None)
            
            if year_data:
                output_dir = os.path.join(dataset_path, f'10K_{year}')
                os.makedirs(output_dir, exist_ok=True)
                
                dropbox_downloader.download(urls=year_data['urls'], output_dir=output_dir)
            else:
                print(f"No data found for 10K_{year}")
            


    async def _watch_efts(self, form=None, cik=None, interval=1, silent=False, callback=None):
        """Watch the EFTS API for changes in the number of filings."""
        params = {
            "startdt": datetime.now().strftime("%Y-%m-%d"),
            "enddt": datetime.now().strftime("%Y-%m-%d")
        }

        if form:
            params["forms"] = ",".join(form) if isinstance(form, list) else form
        else:
            params["forms"] = "-0"

        if cik:
            if isinstance(cik, list):
                params['ciks'] = ','.join(str(c).zfill(10) for c in cik)
            else:
                params['ciks'] = str(cik).zfill(10)

        watch_url = self.generate_url("https://efts.sec.gov/LATEST/search-index", params)
        
        previous_value = None
        async with aiohttp.ClientSession() as session:
            while True:
                data = await self._fetch_json_from_url(session, watch_url)
                
                if data:
                    if not silent:
                        print(f"URL: {watch_url}")
                    
                    current_value = data['hits']['total']['value']
                    
                    if previous_value is not None and current_value != previous_value:
                        if not silent:
                            print(f"Value changed from {previous_value} to {current_value}")
                        if callback:
                            callback(data)
                    
                    previous_value = current_value
                    if not silent:
                        print(f"Current value: {current_value}. Checking again in {interval} seconds.")
                else:
                    print("Error occurred while fetching data.")
                
                await asyncio.sleep(interval)

    def watch(self, interval=1, silent=True, form=None, cik=None, ticker=None, callback=None):
        """
        Monitor SEC EFTS API for new filings in real-time.

        Args:
            interval (int): Seconds between checks. Defaults to 1.
            silent (bool): Suppress progress messages. Defaults to True.
            form (str|list): Form type(s) to watch (e.g., "8-K", ["10-K", "10-Q"])
            cik (str|list): CIK(s) to monitor
            ticker (str): Ticker symbol to monitor (alternative to CIK)
            callback (callable): Function called when new filings detected

        Raises:
            ValueError: If both cik and ticker provided

        Example:
            >>> downloader.watch(form="8-K", ticker="AAPL", callback=lambda x: print(f"New filings: {x}"))
        """
        if sum(x is not None for x in [cik, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik or ticker')
        
        if ticker:
            cik = identifier_to_cik(ticker)

        return asyncio.run(self._watch_efts(interval=interval, silent=silent, form=form, cik=cik, callback=callback))

    async def _download_company_metadata(self):
        # Define file paths
        metadata_file = resource_filename('datamule', 'data/company_metadata.csv')
        former_names_file = resource_filename('datamule', 'data/company_former_names.csv')
        
        # Define temporary file paths
        temp_metadata_file = metadata_file + '.temp'
        temp_former_names_file = former_names_file + '.temp'
        
        metadata_fields = ['cik', 'name', 'entityType', 'sic', 'sicDescription', 'ownerOrg', 
                        'insiderTransactionForOwnerExists', 'insiderTransactionForIssuerExists', 
                        'tickers', 'exchanges', 'ein', 'description', 'website', 'investorWebsite', 
                        'category', 'fiscalYearEnd', 'stateOfIncorporation', 'stateOfIncorporationDescription', 
                        'phone', 'flags', 'mailing_street1', 'mailing_street2', 'mailing_city', 
                        'mailing_stateOrCountry', 'mailing_zipCode', 'mailing_stateOrCountryDescription', 
                        'business_street1', 'business_street2', 'business_city', 'business_stateOrCountry', 
                        'business_zipCode', 'business_stateOrCountryDescription']
        
        former_names_fields = ['cik', 'former_name', 'from_date', 'to_date']
        
        company_tickers = load_package_csv('company_tickers')
        
        async with aiohttp.ClientSession() as session:
            with open(temp_metadata_file, 'w', newline='') as mf, open(temp_former_names_file, 'w', newline='') as fnf:
                metadata_writer = csv.DictWriter(mf, fieldnames=metadata_fields)
                metadata_writer.writeheader()
                
                former_names_writer = csv.DictWriter(fnf, fieldnames=former_names_fields)
                former_names_writer.writeheader()
                
                for company in tqdm(company_tickers, desc="Updating company metadata"):
                    cik = company['cik']
                    url = f'https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json'
                    
                    try:
                        data = await self._fetch_json_from_url(session, url)
                        
                        metadata = {field: data.get(field, '') for field in metadata_fields if field not in ['tickers', 'exchanges']}
                        metadata['cik'] = cik
                        metadata['tickers'] = ','.join(data.get('tickers', []))
                        metadata['exchanges'] = ','.join(data.get('exchanges', []))
                        
                        # Add address information
                        for address_type in ['mailing', 'business']:
                            address = data.get('addresses', {}).get(address_type, {})
                            for key, value in address.items():
                                metadata[f'{address_type}_{key}'] = value if value is not None else ''
                        
                        metadata_writer.writerow(metadata)
                        
                        for former_name in data.get('formerNames', []):
                            former_names_writer.writerow({
                                'cik': cik,
                                'former_name': former_name['name'],
                                'from_date': former_name['from'],
                                'to_date': former_name['to']
                            })
                    
                    except Exception as e:
                        print(f"Error processing CIK {cik}: {str(e)}")
        
        # Now we can safely replace the original files
        
        try:
            # Remove original files if they exist
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
            if os.path.exists(former_names_file):
                os.remove(former_names_file)
            
            # Rename temp files to original names
            os.rename(temp_metadata_file, metadata_file)
            os.rename(temp_former_names_file, former_names_file)
            
            print(f"Metadata successfully updated in {metadata_file}")
            print(f"Former names successfully updated in {former_names_file}")
        except Exception as e:
            print(f"Error occurred while finalizing file update: {str(e)}")
            print("Temporary files have been kept. Please manually review and rename if necessary.")
            return

        # Clean up temp files if they still exist for some reason
        for temp_file in [temp_metadata_file, temp_former_names_file]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    print(f"Warning: Could not remove temporary file {temp_file}: {str(e)}")

    def update_company_metadata(self):
        """
        Update local company metadata files with latest SEC data.

        Downloads current company information including addresses, SIC codes,
        and historical names. Creates/updates CSV files: company_metadata.csv
        and company_former_names.csv.

        Example:
            >>> downloader.update_company_metadata()
        """
        return asyncio.run(self._download_company_metadata())
    
    async def _download_company_tickers(self):
        """Download and process the company tickers JSON file from the SEC."""
        url = 'https://www.sec.gov/files/company_tickers.json'
        
        # Define file paths
        json_file = resource_filename('datamule', 'data/company_tickers.json')
        csv_file = resource_filename('datamule', 'data/company_tickers.csv')
        
        # Define temporary file paths
        temp_json_file = json_file + '.temp'
        temp_csv_file = csv_file + '.temp'

        async with aiohttp.ClientSession() as session:
            try:
                content = await self._fetch_content_from_url(session, url)
                
                # Save the raw JSON file
                await self.write_content_to_file(content, temp_json_file)
                
                # Parse the JSON content
                data = json.loads(content)
                
                # Convert to CSV
                with open(temp_csv_file, 'w', newline='') as csvfile:
                    fieldnames = ['cik', 'ticker', 'title']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for _, company in data.items():
                        writer.writerow({
                            'cik': str(company['cik_str']).zfill(10),
                            'ticker': company['ticker'],
                            'title': company['title']
                        })

                # If everything went well, replace the original files
                if os.path.exists(json_file):
                    os.remove(json_file)
                if os.path.exists(csv_file):
                    os.remove(csv_file)
                
                os.rename(temp_csv_file, csv_file)


                print(f"Company tickers successfully updated in {csv_file}")

            except Exception as e:
                print(f"Error occurred while updating company tickers: {str(e)}")
                print("Temporary files have been kept. Please manually review and rename if necessary.")
                return

            finally:
                # Clean up temp files if they still exist
                for temp_file in [temp_json_file, temp_csv_file]:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except Exception as e:
                            print(f"Warning: Could not remove temporary file {temp_file}: {str(e)}")

    def update_company_tickers(self):
        """
        Update local CIK-to-ticker mapping files.

        Downloads latest company tickers from SEC and updates company_tickers.csv
        with current CIK, ticker, and company name data.

        Example:
            >>> downloader.update_company_tickers()
        """
        asyncio.run(self._download_company_tickers())
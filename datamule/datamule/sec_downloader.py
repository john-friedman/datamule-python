import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import os
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
import requests
import zipfile
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode
import math
from collections import defaultdict
import csv

from .global_vars import headers, dataset_10k_url, dataset_mda_url
from .helper import _download_from_dropbox, identifier_to_cik
from .parsers import parse_company_concepts



class Downloader:
    def __init__(self, rate_limit=10):
        self.global_limiter = AsyncLimiter(rate_limit, 1)
        self.headers = headers  # Define headers in global_vars.py
        self.dataset_path = 'datasets'

    # DONE
    async def _write_file_from_url(self, session, url, output_dir):
        """Asynchronously download a single URL to a specified directory."""
        filename = f"{url.split('/')[7]}_{url.split('/')[-1]}"
        filepath = os.path.join(output_dir, filename)

        for attempt in range(5):
            try:
                async with self.global_limiter:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 429:
                            raise aiohttp.ClientResponseError(response.request_info, response.history, status=429)
                        content = await response.read()
                
                with open(filepath, 'wb') as f:
                    f.write(content)
                return filepath
            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    await asyncio.sleep(5 * (2 ** attempt) + 1)
                else:
                    print(f"Error downloading {url}: {str(e)}")
                    return None
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")
                return None
        return None


    # DONE
    async def _fetch_json_from_url(self, session, url):
        """Asynchronously fetch JSON data from a URL."""
        async with self.global_limiter:
            try:
                async with asyncio.timeout(10):
                    async with session.get(url, headers=self.headers) as response:
                        return await response.json() if response.status == 200 else None
            except Exception as e:
                print(f"Error occurred: {e}")
        return None
    
    # DONE
    async def _download_urls(self, urls, output_dir):
        """Asynchronously download a list of URLs to a specified directory."""
        os.makedirs(output_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            tasks = [self._write_file_from_url(session, url, output_dir) for url in urls]
            results = [await f for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading files")]
        successful_downloads = [result for result in results if result is not None]
        print(f"Successfully downloaded {len(successful_downloads)} out of {len(urls)} URLs")
        return successful_downloads
    
    # WIP
    async def _fetch_json_from_urls(self, urls):
        """Asynchronously fetch JSON data from a list of URLs."""
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_json_from_url(session, url) for url in urls]
            results = [await f for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Fetching data")]
        success = [result for result in results if result is not None]
        print(f"Successfully fetched {len(success)} out of {len(urls)} URLs")
        return success
    

    # DONE
    def run_download_urls(self, urls, output_dir='filings'):
        """Download a list of URLs to a specified directory"""
        return asyncio.run(self._download_urls([url for url in urls if url.split('/')[-1].split('.')[-1] != ''], output_dir))

    # DONE
    async def _get_filing_urls_from_efts(self, base_url):
        """Asynchronously fetch all filing URLs from a given EFTS URL."""
        full_urls = []
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
                        full_urls.extend([f"https://www.sec.gov/Archives/edgar/data/{hit['_source']['ciks'][0]}/{hit['_id'].split(':')[0].replace('-', '')}/{hit['_id'].split(':')[1]}" for hit in hits])
                        if start + page_size > data['hits']['total']['value']:
                            return full_urls
                start += 10 * page_size
        return full_urls

    # DONE
    def _number_of_efts_filings(self, url):
        """Get the number of filings from a given EFTS URL."""
        response = requests.get(url, headers=self.headers)
        return sum(bucket['doc_count'] for bucket in response.json()['aggregations']['form_filter']['buckets'])

    # Possible issue: if more than 10000 filings after filtering, the function will miss some filings.
    # Low priority for now.
    def _subset_urls(self, full_url, total_filings, target_filings_per_range=1000):
        """Split an EFTS URL into multiple URLs based on the number of filings."""
        parsed_url = urlparse(full_url)
        params = parse_qs(parsed_url.query)
        start = datetime.strptime(params.get('startdt', [None])[0], "%Y-%m-%d")
        end = datetime.strptime(params.get('enddt', [None])[0], "%Y-%m-%d")

        # If start and end dates are the same, modify forms
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
                # If forms is not '-0', return the original URL
                return [full_url]

        # If dates are different, proceed with the original logic
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

        # reverse order of urls to download from newest to oldest
        return urls[::-1]

    # DONE
    def _conductor(self, efts_url, return_urls,output_dir):
        """Conduct the download process based on the number of filings."""
        total_filings = self._number_of_efts_filings(efts_url)
        all_primary_doc_urls = []
        
        if total_filings < 10000:
            primary_doc_urls = asyncio.run(self._get_filing_urls_from_efts(efts_url))
            print(f"{efts_url}\nTotal filings: {len(primary_doc_urls)}")
            
            if return_urls:
                return primary_doc_urls
            else:
                self.run_download_urls(urls=primary_doc_urls,output_dir=output_dir)
                return None
        
        for subset_url in self._subset_urls(efts_url, total_filings):
            sub_primary_doc_urls = self._conductor(efts_url=subset_url, return_urls=True,output_dir=output_dir)
            
            if return_urls:
                all_primary_doc_urls.extend(sub_primary_doc_urls)
            else:
                self.run_download_urls(urls=sub_primary_doc_urls,output_dir=output_dir)
        
        return all_primary_doc_urls if return_urls else None

    # DONE. May rename to download_filings
    def download(self, output_dir = 'filings',  return_urls=False,cik=None, ticker=None, form=None, date=None):
        """Download filings based on CIK, ticker, form, and date. Date can be a single date, date range, or list of dates."""
        base_url = "https://efts.sec.gov/LATEST/search-index?"
        if sum(x is not None for x in [cik, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik, name, or ticker')
        
        if ticker is not None:
            cik = identifier_to_cik(ticker)
                
        if cik:
            if isinstance(cik, list):
                formatted_ciks = ','.join(str(c).zfill(10) for c in cik)
            else:
                formatted_ciks = str(cik).zfill(10)
            base_url += f"&ciks={formatted_ciks}"
        
        form_str = f"&forms={','.join(form) if isinstance(form, list) else form}" if form else "&forms=-0"
        
        if isinstance(date, list):
            efts_url_list = [f"{base_url}{form_str}&startdt={d}&enddt={d}" for d in date]
        elif isinstance(date, tuple):
            efts_url_list = [f"{base_url}{form_str}&startdt={date[0]}&enddt={date[1]}"]
        else:
            date_str = f"&startdt={date}&enddt={date}" if date else f"&startdt=2001-01-01&enddt={datetime.now().strftime('%Y-%m-%d')}"
            efts_url_list = [f"{base_url}{form_str}{date_str}"]
        
        all_primary_doc_urls = []
        for efts_url in efts_url_list:
            if return_urls:
                all_primary_doc_urls.extend(self._conductor(efts_url=efts_url, return_urls=True,output_dir=output_dir))
            else:
                self._conductor(efts_url=efts_url, return_urls=False,output_dir=output_dir)
        
        return all_primary_doc_urls if return_urls else None
    
    # TODO add QoL like download all ciks
    # WIP
    def download_company_concepts(self, output_dir = 'company_concepts',cik=None, ticker=None):
        if sum(x is not None for x in [cik, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik, name, or ticker')
        
        if isinstance(ticker, list):
            raise ValueError('Please provide only one ticker')
        elif isinstance(cik, list):
            raise ValueError('Please provide only one cik')
        
        if ticker is not None:
            cik = identifier_to_cik(ticker)
            cik = cik[0]
            

        os.makedirs(output_dir, exist_ok=True)

        if not cik:
            raise ValueError("Please provide a CIK or ticker")

        urls = [f'https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json']
        results = asyncio.run(self._fetch_json_from_urls(urls))
        for result in results:
            table_dict_list = parse_company_concepts(result)

            cik_groups = defaultdict(list)
            for item in table_dict_list:
                cik_groups[item['cik']].append(item)

            for cik, group in cik_groups.items():
                # Create a directory for each CIK
                cik_dir = output_dir + '/' + str(cik)
                os.makedirs(cik_dir, exist_ok=True)

                # Create a set to track unique facts for metadata
                unique_facts = set()

                # Write table CSV files
                for item in group:
                    fact = item['fact']
                    unique_facts.add(fact)
                    filename = f"{fact}.csv"
                    filepath = os.path.join(cik_dir, filename)
                    with open(filepath, 'w', newline='') as csvfile:
                        # Assuming all dictionaries in the list have the same keys
                        fieldnames = item['table'][0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        
                        # Write the header
                        writer.writeheader()
                        
                        # Write the rows
                        for row in item['table']:
                            writer.writerow(row)

                # Write metadata CSV file
                metadata_filename = f"{cik}_metadata.csv"
                metadata_filepath = os.path.join(cik_dir, metadata_filename)

                with open(metadata_filepath, 'w', newline='') as csvfile:
                    fieldnames = ['fact', 'category', 'label', 'description', 'unit', 'table']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for item in group:
                        if item['fact'] in unique_facts:
                            writer.writerow({
                                'fact': item['fact'],
                                'category': item['category'],
                                'label': item['label'],
                                'description': item['description'],
                                'unit': item['unit'],
                                'table': item['fact']  # Using 'fact' as table name
                            })
                            unique_facts.remove(item['fact'])

        print(f"Downloaded company concepts to {output_dir}")

        

    # DONE. Add more datasets
    def download_dataset(self, dataset, dataset_path='datasets'):
        """Download a dataset from Dropbox. Currently supports '10K' and 'MDA'."""
        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)

        if dataset == '10K':
            file_path = os.path.join(dataset_path, '10K.zip')
            _download_from_dropbox(dataset_10k_url, file_path)
        elif dataset == "MDA":
            file_path = os.path.join(dataset_path, 'MDA.zip')
            _download_from_dropbox(dataset_mda_url, file_path)

    # DONE. May need simplification
    async def _watch_efts(self, form=None, cik=None, interval=1, silent=False):
        """Watch the EFTS API for changes in the number of filings."""
        params = {
            "startdt": (datetime.now()).strftime("%Y-%m-%d"),
            "enddt": datetime.now().strftime("%Y-%m-%d")
        }

        # Handle forms parameter
        if form:
            if isinstance(form, str):
                params["forms"] = form
            elif isinstance(form, list):
                params["forms"] = ",".join(form)
            else:
                raise ValueError("forms must be a string or a list of strings")
        else:
            params["forms"] = "-0"  # Default value if no forms specified

        # Handle cik parameter
        if cik:
            if isinstance(cik, list):
                params['ciks'] = ','.join(str(c).zfill(10) for c in cik)
        else:
            pass

        previous_value = None
        watch_url = "https://efts.sec.gov/LATEST/search-index" + "?" + urlencode(params)
        
        async with aiohttp.ClientSession() as session:
                while True:
                    data = await self._fetch_json_from_url(session, watch_url)
                    
                    if data:
                        if not silent:
                            print(f"URL: {watch_url}?{urlencode(params)}")
                        
                        current_value = data['hits']['total']['value']
                        
                        if previous_value is not None and current_value != previous_value:
                            if not silent:
                                print(f"Value changed from {previous_value} to {current_value}")
                            return True
                        
                        previous_value = current_value
                        if not silent:
                            print(f"Current value: {current_value}. Checking again in {interval} seconds.")
                    else:
                        print("Error occurred while fetching data.")
                    
                    await asyncio.sleep(interval)

    # DONE. May add return results option in the future
    def watch(self,interval=1,silent=True, form=None,cik=None, ticker=None):
        """Watch the EFTS API for changes in the number of filings."""
        if sum(x is not None for x in [cik, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik, name, or ticker')
        
        if ticker:
            cik = identifier_to_cik(ticker)

        return asyncio.run(self._watch_efts(interval=interval,silent=silent,form=form,cik=cik))
    
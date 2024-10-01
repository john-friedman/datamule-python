import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import os
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode
import math
import re

from .global_vars import headers, dataset_10k_url, dataset_mda_url, dataset_xbrl_url, dataset_10k_record_list
from .helper import _download_from_dropbox, identifier_to_cik, load_company_tickers
from .zenodo_downloader import download_from_zenodo


class Downloader:
    def __init__(self, rate_limit=10):
        self.global_limiter = AsyncLimiter(rate_limit, 1)
        self.headers = headers  # Define headers in global_vars.py
        self.dataset_path = 'datasets'

    # WIP. generalize
    # we could add filepath here
    async def _write_file_from_url(self, session, url, output_dir,temp_fix=None):
        """Asynchronously download a single URL to a specified directory."""

        # this is issue preventing generalization

        # workaround
        if temp_fix is None:
            filename = f"{url.split('/')[7]}_{url.split('/')[-1]}"
            filepath = os.path.join(output_dir, filename)
        else:
            filename = f"{url.split('/')[-1]}"
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
    async def _download_urls(self, urls, output_dir,temp_fix=None):
        """Asynchronously download a list of URLs to a specified directory."""
        os.makedirs(output_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            tasks = [self._write_file_from_url(session=session, url=url, output_dir=output_dir,temp_fix=temp_fix) for url in urls]
            results = [await f for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading files")]
        successful_downloads = [result for result in results if result is not None]
        print(f"Successfully downloaded {len(successful_downloads)} out of {len(urls)} URLs")
        return successful_downloads
    

    # DONE
    def run_download_urls(self, urls, output_dir='filings',temp_fix=None):
        """Download a list of URLs to a specified directory"""
        return asyncio.run(self._download_urls([url for url in urls if url.split('/')[-1].split('.')[-1] != ''], output_dir,temp_fix=temp_fix))

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
    
    # DONE
    def download_company_concepts(self, output_dir = 'company_concepts',cik=None, ticker=None):
        if sum(x is not None for x in [cik, ticker]) > 1:
            raise ValueError('Please provide no more than one identifier: cik, name, or ticker')
        
        ciks = None
        if cik:
            if isinstance(cik, list):
                ciks = cik
            else:
                ciks = [cik]
        
        if ticker is not None:
            ciks = identifier_to_cik(ticker)

        # load all company ciks from company tickers
        if ciks is None:
            company_tickers = load_company_tickers()
            ciks = [company['cik'] for company in company_tickers]
            
        os.makedirs(output_dir, exist_ok=True)
                

        urls = [f'https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json' for cik in ciks]
        self.run_download_urls(urls=urls,output_dir=output_dir,temp_fix='company_concepts')

    # WIP
    def download_dataset(self, dataset, dataset_path='datasets'):
        """Download a dataset from Dropbox. Currently supports 'parsed_10k' and 'mda'."""
        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)

        if dataset == 'parsed_10k':
            file_path = os.path.join(dataset_path, '10K.zip')
            _download_from_dropbox(dataset_10k_url, file_path)
        elif dataset == "mda":
            file_path = os.path.join(dataset_path, 'MDA.zip')
            _download_from_dropbox(dataset_mda_url, file_path)
        elif dataset == "xbrl":
            file_path = os.path.join(dataset_path, 'XBRL.zip')
            _download_from_dropbox(dataset_xbrl_url, file_path)
        elif re.match(r"10k_(\d{4})$", dataset):
            year = dataset.split('_')[-1]
            record = next((record['record'] for record in dataset_10k_record_list if record['year'] == int(year)), None)
            out_path = os.path.join(dataset_path, '10K') 
            download_from_zenodo(record, out_path)

            

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
    
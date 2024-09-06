import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
import random
import os
from global_vars import headers
import pandas as pd
from helper import construct_primary_doc_url

class Downloader:
    def __init__(self, rate_limit=10):
        self.rate_limit = rate_limit
        self.limiter = AsyncLimiter(rate_limit, 1)  # rate_limit requests per second
        self.headers = headers

    def set_headers(self, headers):
        self.headers = headers

    async def _download_url(self, session, url, output_dir):
        max_retries = 5
        base_delay = 5

        filename = url.split('/')[-1]
        filepath = os.path.join(output_dir, filename)

        for attempt in range(max_retries):
            try:
                async with self.limiter:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 429:  # Too Many Requests
                            raise aiohttp.ClientResponseError(response.request_info, response.history, status=429)
                        content = await response.read()

                with open(filepath, 'wb') as f:
                    f.write(content)
                
                print(f"Downloaded: {url}")
                return filepath

            except aiohttp.ClientResponseError as e:
                if e.status == 429:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limited. Retrying {url} in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    print(f"Error downloading {url}: {str(e)}")
                    return None
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")
                return None

        print(f"Max retries reached for {url}")
        return None

    async def _download_urls(self, urls, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                task = asyncio.create_task(self._download_url(session, url, output_dir))
                tasks.append(task)

            results = await asyncio.gather(*tasks)

        successful_downloads = [result for result in results if result is not None]
        print(f"Successfully downloaded {len(successful_downloads)} out of {len(urls)} URLs")
        return successful_downloads

    def run_download_urls(self, urls, output_dir='data'):
        return asyncio.run(self._download_urls(urls, output_dir))
    
    def download(self,output_dir='filings', form=None, date=None, cik=None, name=None, ticker=None):
        # load data from index
        filings_index = pd.read_csv('data/filings_index.csv')
        submissions_index = pd.read_csv('data/submissions_index.csv')
        company_tickers = pd.read_csv('data/company_tickers.csv')

        # check there is only one identifier
        if sum(x is not None for x in [cik, name, ticker]) > 1:
            raise ValueError('Please provide exactly one identifier: cik, name, or ticker')
        
        if form:
            # check if form is list
            if not isinstance(form, list):
                form = [form]
            
            # subset submissions_index by forms in form
            submissions_index = submissions_index[submissions_index['form'].isin(form)]

        if date:
            # convert date(s) to datetime
            def to_datetime(d):
                return pd.to_datetime(d).date() if isinstance(d, str) else d

            if isinstance(date, tuple) and len(date) == 2:
                # date range
                start_date, end_date = map(to_datetime, date)
                mask = (filings_index['filing_date'] >= start_date) & (filings_index['filing_date'] <= end_date)
                filings_index = filings_index[mask]
            elif isinstance(date, list):
                # list of dates
                dates = list(map(to_datetime, date))
                filings_index = filings_index[filings_index['filing_date'].isin(dates)]
            else:
                # single date
                single_date = to_datetime(date)
                filings_index = filings_index[filings_index['filing_date'] == single_date]

        if cik:
            if isinstance(cik, list):
                # list of CIKs

                # convert ciks to int
                cik = list(map(int, cik))
                submissions_index = submissions_index[submissions_index['cik'].isin(cik)]
            else:
                # single CIK
                cik = int(cik)
                submissions_index = submissions_index[submissions_index['cik'] == cik]
        
        if name:
            # subset company_tickers by name
            matched_companies = company_tickers[company_tickers['title'].str.contains(name, case=False)]
            ciks = matched_companies['cik'].tolist()
            # subset submissions_index by cik
            submissions_index = submissions_index[submissions_index['cik'].isin(ciks)]

        if ticker:
            # subset company_tickers by ticker
            matched_companies = company_tickers[company_tickers['ticker'] == ticker.upper()]
            ciks = matched_companies['cik'].tolist()
            # subset submissions_index by cik
            submissions_index = submissions_index[submissions_index['cik'].isin(ciks)]

        # from submissions index select unique filing_entity, accepted_year, filing_count tuples
        unique_submissions = submissions_index[['filing_entity', 'accepted_year', 'filing_count']].drop_duplicates()

        # for each tuple, get the corresponding primary_doc_url from filings_index
        primary_doc_urls = []
        for _, row in unique_submissions.iterrows():
            matching_filing = filings_index[
                (filings_index['filing_entity'] == row['filing_entity']) &
                (filings_index['accepted_year'] == row['accepted_year']) &
                (filings_index['filing_count'] == row['filing_count'])
            ]
            if not matching_filing.empty:
                # fix
                primary_doc_url = construct_primary_doc_url(cik,filing_entity,accepted_year,filing_count,primary_doc_url):
                primary_doc_urls.append(matching_filing.iloc[0]['primary_doc_url'])

        
        # download all primary_doc_url
        self.run_download_urls(primary_doc_urls, output_dir)
import time
from collections import deque
from .eftsquery import query_efts
from datetime import datetime
from ..utils import headers
import urllib.request
import xml.etree.ElementTree as ET
import re
from ..utils import PreciseRateLimiter
from .eftsquery import EFTSQuery
import asyncio

def poll_rss():
    base_url = 'https://www.sec.gov/cgi-bin/browse-edgar?count=100&action=getcurrent&output=rss'
    req = urllib.request.Request(base_url, headers=headers)
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
    
    root = ET.fromstring(content)
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    entries = root.findall('atom:entry', namespace)
    grouped = {}

    for entry in entries:
        url = entry.find('atom:link', namespace).get('href')
        accession = re.search(r'/(\d{10})-(\d{2})-(\d{6})', url)
        accession = accession.group(1) + accession.group(2) + accession.group(3)
        cik = re.search(r'/data/(\d+)/', url).group(1)
        
        if accession not in grouped:
            grouped[accession] = {'submission_type': '', 'ciks': set(), 'filing_date': ''}
        
        grouped[accession]['ciks'].add(cik)
        grouped[accession]['submission_type'] = entry.find('atom:category', namespace).get('term')
        summary_text = entry.find('atom:summary', namespace).text
        filing_date_match = re.search(r'Filed:</b>\s*(\d{4}-\d{2}-\d{2})', summary_text)
        if filing_date_match:
            grouped[accession]['filing_date'] = filing_date_match.group(1)

    results = [{'accession': int(k.replace('-', '')), 'submission_type': v['submission_type'], 'ciks': list(v['ciks']), 'filing_date': v['filing_date']} for k, v in grouped.items()]
    return results

def clean_efts_hits(hits):
    # clean hits
    hits = [{'accession': int(hit['_source']['adsh'].replace('-','')), 'filing_date': hit['_source']['file_date'], 'ciks': hit['_source']['ciks']} for hit in hits]
    return hits

class Monitor():
    def __init__(self):
        self.accessions = deque(maxlen=50000)
        self.ratelimiters = {'sec.gov':PreciseRateLimiter(rate=5)}
        self.efts_query = EFTSQuery()
        self.efts_query.limiter = self.ratelimiters['sec.gov']

    def set_domain_rate_limit(self, domain, rate):
        self.ratelimiters[domain] = PreciseRateLimiter(rate=rate)
        if domain == 'sec.gov':
            self.efts_query.limiter = self.ratelimiters[domain]

    def monitor_submissions(self, data_callback=None, interval_callback=None,
                            polling_interval=1000, quiet=True, start_date=None,
                            validation_interval=60000):
        """
        Monitor SEC submissions using the EDGAR system.
        :param data_callback: function to call with the data
        :param interval_callback: function that executes between polls
        :param polling_interval: interval between polls in milliseconds
        :param requests_per_second: number of requests per second to make.
        :param quiet: if True, suppresses output
        :param start_date: backfill start date in YYYY-MM-DD format
        :param validation_interval: interval between validation in milliseconds

        This function combines the speed of the RSS feed (fast, but misses some submissions) with the accuracy of the EFTS system.
        """
    
        last_validation_time = 0

        # Backfill if start_date is provided
        if start_date is not None:
            today_date = datetime.now().date()
            if not quiet:
                print(f"Backfilling from {start_date} to {today_date}")

            hits = clean_efts_hits(query_efts(filing_date=(start_date, today_date),quiet=quiet))

            new_hits = self._filter_new_accessions(hits)
            if not quiet:
                print(f"New submissions found: {len(new_hits)}")
            if new_hits and data_callback:
                data_callback(new_hits)



        while True:
            current_time = time.time()
            # RSS polling
            if not quiet:
                print(f"Polling RSS feed")
            results = poll_rss()
            new_results = self._filter_new_accessions(results)
            if new_results:
                if not quiet:
                    print(f"Found {len(new_results)} new submissions via RSS")
                if data_callback:
                    data_callback(new_results)
            
            # EFTS validation
            if validation_interval and (current_time - last_validation_time) >= validation_interval/1000:
                # Get submissions from the last 24 hours for validation
                today_date = (datetime.now()).strftime('%Y-%m-%d')
                if not quiet:
                    print(f"Validating submissions from {today_date}")

                hits = clean_efts_hits(query_efts(filing_date=(today_date, today_date),quiet=quiet))
                new_hits = self._filter_new_accessions(hits)
                if new_hits:
                    if not quiet:
                        print(f"Found {len(new_hits)} new submissions via EFTS validation")
                    if data_callback:
                        data_callback(new_hits)
                last_validation_time = current_time
            
            # Interval callback
            if interval_callback:
                interval_callback()
            
            # Sleep to control the polling rate
            time.sleep(polling_interval/1000)
                

    
    def _filter_new_accessions(self, items):
        """Filter items to only include those with new accession numbers."""
        new_items = []
        for item in items:
            accession = item['accession']
            if accession not in self.accessions:
                self.accessions.append(accession)
                new_items.append(item)
        return new_items
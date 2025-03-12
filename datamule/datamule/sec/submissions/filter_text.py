import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode
from tqdm import tqdm
from collections import deque
from .eftsquery import EFTSQuery

# Assuming all the classes from your original code are here
# This code adds the TextSearchEFTSQuery class and filter_text function

class TextSearchEFTSQuery(EFTSQuery):
    def __init__(self, text_query, requests_per_second=5.0):
        super().__init__(requests_per_second=requests_per_second)
        self.text_query = text_query
        
    def _prepare_params(self, cik=None, submission_type=None, filing_date=None):
        # Get base parameters from parent class
        params = super()._prepare_params(cik, submission_type, filing_date)
        
        # Add text query parameter
        params['q'] = self.text_query
        
        return params

async def extract_accession_numbers(hits):
    """Extract accession numbers from hits"""
    accession_numbers = []
    for hit in hits:
        if '_id' in hit:
            # Extract accession number (part before the colon)
            doc_id = hit['_id']
            if ':' in doc_id:
                acc_no = doc_id.split(':')[0]
                accession_numbers.append(acc_no)
    return accession_numbers

def filter_text(text_query, cik=None, submission_type=None, filing_date=None, requests_per_second=5.0):
    """
    Search SEC filings for text and return matching accession numbers.
    
    Parameters:
    -----------
    text_query : str
        The text to search for in filings. To search for an exact phrase, use double quotes.
        Example: 'covid' or '"climate change"'
    cik : str, list, optional
        CIK number(s) to filter by. Will be zero-padded to 10 digits.
    submission_type : str, list, optional
        Filing type(s) to filter by (e.g., '10-K', '10-Q').
        Defaults to '-0' for primary documents only.
    filing_date : str, tuple, list, optional
        Date or date range to filter by. Can be a single date string ('YYYY-MM-DD'),
        a tuple of (start_date, end_date), or a list of dates.
    requests_per_second : float, optional
        Maximum number of requests per second to make to the SEC API.
        Default is 5.0.
        
    Returns:
    --------
    list
        List of accession numbers (as strings) for filings that match the text query.
    """
    async def run_query():
        query = TextSearchEFTSQuery(text_query, requests_per_second=requests_per_second)
        
        # Create a collector for accession numbers
        all_acc_nos = []
        
        async def collect_acc_nos(hits):
            acc_nos = await extract_accession_numbers(hits)
            all_acc_nos.extend(acc_nos)
        
        # Run the query with our callback
        await query.query(cik, submission_type, filing_date, collect_acc_nos)
        
        return all_acc_nos
    
    return asyncio.run(run_query())


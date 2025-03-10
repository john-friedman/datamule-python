from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from .submission import Submission
from .seclibrary.downloader import download as seclibrary_download
from .sec.downloader import download as sec_download
from .sec.filter_text import filter_text
from .config import Config
import os
from .helper import get_cik_from_dataset, get_ciks_from_metadata_filters

class Portfolio:
    def __init__(self, path):
        self.path = Path(path)
        self.submissions = []
        self.MAX_WORKERS = os.cpu_count() - 1 
        
        if self.path.exists():
            self._load_submissions()
        else:
            self.path.mkdir(parents=True, exist_ok=True)
    
    def _load_submissions(self):
        folders = [f for f in self.path.iterdir() if f.is_dir()]
        print(f"Loading {len(folders)} submissions")
        
        def load_submission(folder):
            try:
                return Submission(folder)
            except Exception as e:
                print(f"Error loading submission from {folder}: {str(e)}")
                return None
        
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            self.submissions = list(tqdm(
                executor.map(load_submission, folders),
                total=len(folders),
                desc="Loading submissions"
            ))
            
        # Filter out None values from failed submissions
        self.submissions = [s for s in self.submissions if s is not None]
        print(f"Successfully loaded {len(self.submissions)} submissions")

    def process_submissions(self, callback):
        """Process all submissions using a thread pool."""
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            results = list(tqdm(
                executor.map(callback, self.submissions),
                total=len(self.submissions),
                desc="Processing submissions"
            ))
            return results

    def process_documents(self, callback):
        """Process all documents using a thread pool."""
        documents = [doc for sub in self.submissions for doc in sub]
        
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            results = list(tqdm(
                executor.map(callback, documents),
                total=len(documents),
                desc="Processing documents"
            ))
            return results
    
    def _process_cik_and_metadata_filters(self, cik=None, ticker=None, **kwargs):
        """
        Helper method to process CIK, ticker, and metadata filters.
        Returns a list of CIKs after processing.
        """
        # Input validation
        if cik is not None and ticker is not None:
            raise ValueError("Only one of cik or ticker should be provided, not both.")

        # Convert ticker to CIK if provided
        if ticker is not None:
            cik = get_cik_from_dataset('company_tickers', 'ticker', ticker)

        # Normalize CIK format
        if cik is not None:
            if isinstance(cik, str):
                cik = [int(cik)]
            elif isinstance(cik, int):
                cik = [cik]
            elif isinstance(cik, list):
                cik = [int(x) for x in cik]

        # Process metadata filters if provided
        if kwargs:
            metadata_ciks = get_ciks_from_metadata_filters(**kwargs)

            if cik is not None:
                cik = list(set(cik).intersection(metadata_ciks))
            else:
                cik = metadata_ciks
                
        return cik
        
    def filter_text(self, text_query, cik=None, ticker=None, submission_type=None, filing_date=None, **kwargs):
        """
        Filter text based on query and various parameters.
        When called multiple times, takes the intersection of results.
        Now supports metadata filters through kwargs.
        """
        # Process CIK and metadata filters
        cik = self._process_cik_and_metadata_filters(cik, ticker, **kwargs)
        
        # Call the filter_text function with processed parameters
        new_accession_numbers = filter_text(
            text_query=text_query,
            cik=cik,
            submission_type=submission_type,
            filing_date=filing_date
        )
        
        # If we already have accession numbers, take the intersection
        if hasattr(self, 'accession_numbers') and self.accession_numbers:
            self.accession_numbers = list(set(self.accession_numbers).intersection(new_accession_numbers))
        else:
            # First query, just set the accession numbers
            self.accession_numbers = new_accession_numbers

    def download_submissions(self, cik=None, ticker=None, submission_type=None, filing_date=None, provider=None, **kwargs):
        if provider is None:
            config = Config()
            provider = config.get_default_source()

        # Process CIK and metadata filters
        cik = self._process_cik_and_metadata_filters(cik, ticker, **kwargs)

        if provider == 'datamule':
            seclibrary_download(
                output_dir=self.path,
                cik=cik,
                submission_type=submission_type,
                filing_date=filing_date,
                accession_numbers=self.accession_numbers if hasattr(self, 'accession_numbers') else None
            )
        else:
            sec_download(
                output_dir=self.path,
                cik=cik,
                submission_type=submission_type,
                filing_date=filing_date,
                requests_per_second=4, # Revisit this later.
                accession_numbers=self.accession_numbers if hasattr(self, 'accession_numbers') else None
            )
        
        # Reload submissions after download
        self._load_submissions()
        
    def __iter__(self):
        return iter(self.submissions)
    
    def document_type(self, document_types):
        """Filter documents by type(s)."""
        if isinstance(document_types, str):
            document_types = [document_types]
            
        for submission in self.submissions:
            yield from submission.document_type(document_types)
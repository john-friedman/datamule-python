from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from .submission import Submission
from .olddownloader.premiumdownloader import PremiumDownloader
from .downloader.downloader import download
from .config import Config
import os

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

    def download_submissions(self, cik=None, ticker=None, submission_type=None, filing_date=None, provider=None):
        if provider is None:
            config = Config()
            provider = config.get_default_source()


        if provider == 'datamule':
            downloader = PremiumDownloader()
            downloader.download_submissions(
                output_dir=self.path,
                cik=cik,
                ticker=ticker,
                submission_type=submission_type,
                filing_date=filing_date
            )
        else:
            download(
                output_dir=self.path,
                cik=cik,
                submission_type=submission_type,
                filing_date=filing_date,
                requests_per_second=4 # change this
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

    def contains_string(self, pattern, document_types=None):
        """Search for pattern in documents, with optional type filter."""
        def check_document(document):
            return document if document.contains_string(pattern) else None
        
        # Get documents, filtered by type if specified
        documents = list(self.document_type(document_types)) if document_types else [
            doc for sub in self.submissions for doc in sub
        ]
        
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            results = executor.map(check_document, documents)
            
            for doc in tqdm(results, total=len(documents), desc=f"Searching for '{pattern}'"):
                if doc is not None:
                    yield doc
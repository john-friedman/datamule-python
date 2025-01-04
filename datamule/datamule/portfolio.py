from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from .submission import Submission
from .downloader.premiumdownloader import PremiumDownloader
from .downloader.downloader import Downloader
from .config import Config

class Portfolio:
    def create(cls, path):
        # This method handles the process pool lifecycle
        with ProcessPoolExecutor() as executor:
            portfolio = cls(path, executor)
            return portfolio

    def __init__(self, path, executor=None):
        self.path = Path(path)
        # check if path exists
        if self.path.exists():
            folders = [f for f in self.path.iterdir() if f.is_dir()]
            print(f"Loading {len(folders)} submissions")
            
            if executor is None:
                # Fall back to sequential loading if no executor
                self.submissions = [Submission(f) for f in tqdm(folders, desc="Loading submissions")]
            else:
                # Use provided executor for parallel loading
                self.submissions = list(tqdm(
                    executor.map(Submission, folders),
                    total=len(folders),
                    desc="Loading submissions"  
                ))
            
        else:
            pass

    def download_submissions(self, cik=None, ticker=None, submission_type=None, filing_date=None, provider=None):
        if provider is None:
            config = Config()
            provider = config.get_default_source()

        if provider == 'sec':
            downloader = Downloader()
        elif provider == 'datamule':
            downloader = PremiumDownloader()

        downloader.download_submissions(output_dir=self.path, cik=cik, ticker=ticker, submission_type=submission_type, filing_date=filing_date
                                        )
    def __iter__(self):
        return iter(self.submissions)
    
    def document_type(self, document_types):
        # Convert single document type to list for consistent handling
        if isinstance(document_types, str):
            document_types = [document_types]
            
        for submission in self.submissions:
            yield from submission.document_type(document_types)

    def contains_string(self, pattern, document_types=None, executor=None):
        def check_document(document):
            return document if document.contains_string(pattern) else None
        
        documents = list(self.document_type(document_types) if document_types else (
            doc for sub in tqdm(self.submissions, desc="Collecting documents") for doc in sub
        ))
        
        if executor:
            results = list(tqdm(
                executor.map(check_document, documents),
                total=len(documents),
                desc=f"Searching for '{pattern}'"
            ))
            yield from (doc for doc in results if doc is not None)
        else:
            for document in tqdm(documents, desc=f"Searching for '{pattern}'"):
                if document.contains_string(pattern):
                    yield document
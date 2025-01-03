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

        downloader.download_submissions(output_dir=self.path, cik=cik, ticker=ticker, submission_type=submission_type, filing_date=filing_date)
    def __iter__(self):
        return iter(self.submissions)
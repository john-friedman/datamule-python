from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from .submission import Submission

class Portfolio:
    @classmethod
    def create(cls, path):
        # This method handles the process pool lifecycle
        with ProcessPoolExecutor() as executor:
            portfolio = cls(path, executor)
            return portfolio

    def __init__(self, path, executor=None):
        self.path = Path(path)
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

    def __iter__(self):
        return iter(self.submissions)
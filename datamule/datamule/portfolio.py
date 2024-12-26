from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from .submission import Submission

class Portfolio:
    def __init__(self, path):
        self.path = Path(path)
        folders = [f for f in self.path.iterdir() if f.is_dir()]
        print(f"Loading {len(folders)} submissions")
        # Load submissions in parallel
        with ProcessPoolExecutor() as executor:
            # Show progress while loading
            self.submissions = list(tqdm(
                executor.map(Submission, folders),
                total=len(folders),
                desc="Loading submissions"  
            ))

    def __iter__(self):
        return iter(self.submissions)
from pathlib import Path
from .submission import Submission

class Portfolio:
    def __init__(self, path):
        self.path = Path(path)
        self.submissions = []
        
        # Load all subdirectories as submissions
        for folder in self.path.iterdir():
            if folder.is_dir():
                self.submissions.append(Submission(folder))


    def __iter__(self):
        return iter(self.submissions)
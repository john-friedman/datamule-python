from pathlib import Path


# we need to pass in metadata from submissions.
class Document():
    def __init__(self,path):
        self.path = Path(path)

    def _load_document(self):
        with self.path.open('r') as f:
            self.content = f.read()

    def _parse_document(self):
        # we implement generalized parsing here.
        raise NotImplementedError

    def parse(self):
        self._load_document()
        self._parse_document()

    # add iterable here to allow to pass into pandas, polars, etc.
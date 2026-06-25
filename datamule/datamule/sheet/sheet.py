from pathlib import Path
import os

from datamulehub import databases


class Sheet:
    def __init__(self, path, api_key=None):
        self.path = Path(path)
        self._api_key = api_key

    @property
    def api_key(self):
        return getattr(self, "_api_key", None) or os.getenv("DATAMULE_API_KEY")

    @api_key.setter
    def api_key(self, value):
        if not value:
            raise ValueError("API key cannot be empty")
        self._api_key = value

    def get_table(self, query, output_dir=None, wait_seconds=None):
        destination = Path(output_dir) if output_dir is not None else self.path
        return databases.query(
            query,
            output_dir=destination,
            api_key=self.api_key,
            wait_seconds=wait_seconds,
        )

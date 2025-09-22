from .submission.submission import Submission
from .portfolio.portfolio import Portfolio
from .document.document import Document
from .helper import _load_package_csv, load_package_dataset
from .config import Config
from .sheet.sheet import Sheet
from .index import Index
from .package_updater import PackageUpdater
from .utils.format_accession import format_accession
from .utils.construct_submissions_data import construct_submissions_data
from .book.book import Book


# Keep the notebook environment setup
def _is_notebook_env():
    """Check if the code is running in a Jupyter or Colab environment."""
    try:
        shell = get_ipython().__class__.__name__
        return shell in ('ZMQInteractiveShell', 'Shell', 'Google.Colab')
    except NameError:
        return False

from functools import lru_cache

@lru_cache(maxsize=1)
def _setup_notebook_env():
    """Setup Jupyter/Colab-specific configurations if needed."""
    if _is_notebook_env():
        import nest_asyncio
        nest_asyncio.apply()

# Set up notebook environment
_setup_notebook_env()


# TODO, is this load bearing?
__all__ = [
    '_load_package_csv',
    'load_package_dataset',
    'Portfolio',
    'Submission',
    'Document',
    'Config',
    'Sheet',
    'Index',
    'PackageUpdater',
]
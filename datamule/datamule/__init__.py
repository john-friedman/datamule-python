from .submission import Submission
from .portfolio import Portfolio
from .document.document import Document
from .helper import _load_package_csv, load_package_dataset
from .config import Config
from .sheet import Sheet
from .index import Index
from .package_updater import PackageUpdater



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
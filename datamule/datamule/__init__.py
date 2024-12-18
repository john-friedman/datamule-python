import sys
from importlib.util import find_spec
from functools import lru_cache

def __getattr__(name):
    if name == 'Downloader':
        from .downloader.downloader import Downloader
        return Downloader
    elif name == 'PremiumDownloader':
        from .downloader.premiumdownloader import PremiumDownloader
        return PremiumDownloader
    elif name == 'Parser':
        from .parser.document_parsing.sec_parser import Parser
        return Parser
    elif name == 'Monitor':
        from .monitor import Monitor
        return Monitor
    elif name == 'PackageUpdater':
        from .packageupdater import PackageUpdater
        return PackageUpdater
    elif name == 'Submission':
        from .submission import Submission
        return Submission
    elif name == 'Portfolio':
        from .portfolio import Portfolio
        return Portfolio
    elif name == 'Document':
        from .document import Document
        return Document
    elif name == "parse_sgml_submission":
        from .parser.sgml_parsing.sgml_parser_cy import parse_sgml_submission
        return parse_sgml_submission
    elif name == 'DatasetBuilder':
        from .dataset_builder import DatasetBuilder
        return DatasetBuilder
    elif name == 'load_package_csv':
        from .helper import load_package_csv
        return load_package_csv
    elif name == 'load_package_dataset':
        from .helper import load_package_dataset
        return load_package_dataset
    raise AttributeError(f"module 'datamule' has no attribute '{name}'")

# Lazy load nest_asyncio only when needed
def _is_notebook_env():
    """Check if the code is running in a Jupyter or Colab environment."""
    try:
        shell = get_ipython().__class__.__name__
        return shell in ('ZMQInteractiveShell', 'Shell', 'Google.Colab')
    except NameError:
        return False

@lru_cache(maxsize=1)
def _setup_notebook_env():
    """Setup Jupyter/Colab-specific configurations if needed."""
    if _is_notebook_env():
        import nest_asyncio
        nest_asyncio.apply()

# Set up notebook environment
_setup_notebook_env()

__all__ = [
    'Downloader',
    'PremiumDownloader',
    'load_package_csv',
    'load_package_dataset',
    'Parser',
    'Filing',
    'DatasetBuilder'
]
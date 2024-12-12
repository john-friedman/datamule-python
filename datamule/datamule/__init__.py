# datamule/__init__.py
import sys
from importlib.util import find_spec
from functools import lru_cache

def __getattr__(name):
    if name == 'Downloader':
        from .downloader.downloader import Downloader
        return Downloader
    elif name == 'parse_textual_filing':
        from .parser.sgml_parsing.sgml_parser_cy import parse_sgml_submission
        return parse_sgml_submission
    elif name == 'Parser':
        from .parser.document_parsing.sec_parser import Parser
        return Parser
    elif name == 'Filing':
        from .submission import Submission
        return Submission
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
    'load_package_csv',
    'load_package_dataset',
    'Parser',
    'Filing',
    'DatasetBuilder'
]
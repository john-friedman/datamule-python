# datamule/__init__.py
import sys
from importlib.util import find_spec
from functools import lru_cache

# Lazy load nest_asyncio only when needed
def _setup_jupyter():
    """Setup Jupyter-specific configurations if needed."""
    if _is_jupyter():
        import nest_asyncio
        nest_asyncio.apply()

def _is_jupyter():
    """Check if the code is running in a Jupyter environment."""
    try:
        shell = get_ipython().__class__.__name__
        return shell == 'ZMQInteractiveShell'
    except NameError:
        return False

# Lazy loading for main components
@lru_cache(None)
def get_downloader():
    from .downloader.sec_downloader import Downloader
    return Downloader

@lru_cache(None)
def get_parser():
    from .parser.sec_parser import Parser
    return Parser

@lru_cache(None)
def get_filing():
    from .sec_filing import Filing
    return Filing

@lru_cache(None)
def get_dataset_builder():
    if find_spec('pandas') is not None:
        try:
            from .dataset_builder.dataset_builder import DatasetBuilder
            return DatasetBuilder
        except ImportError:
            return None
    return None

# Helper functions that can be imported directly
from .datamule_api import parse_textual_filing
from .helper import load_package_csv, load_package_dataset
from .global_vars import *
from .parser.sgml_parser import parse_submission

# Define classes with delayed initialization
class Downloader:
    def __new__(cls, *args, **kwargs):
        return get_downloader()(*args, **kwargs)

class Parser:
    def __new__(cls, *args, **kwargs):
        return get_parser()(*args, **kwargs)

class Filing:
    def __new__(cls, *args, **kwargs):
        return get_filing()(*args, **kwargs)

class DatasetBuilder:
    def __new__(cls, *args, **kwargs):
        builder_cls = get_dataset_builder()
        if builder_cls is None:
            raise ImportError(
                "DatasetBuilder requires pandas. "
                "Install with: pip install datamule[dataset_builder]"
            )
        return builder_cls(*args, **kwargs)

# Set up Jupyter support only when imported
_setup_jupyter()

__all__ = [
    'Downloader',
    'parse_textual_filing',
    'load_package_csv',
    'load_package_dataset',
    'Parser',
    'Filing',
    'DatasetBuilder'
]
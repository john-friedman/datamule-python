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

# Rework imports, we also need to setup lazy loading
from .helper import load_package_csv, load_package_dataset
from .parser.sgml_parsing.sgml_parser_cy import parse_sgml_submission
from .submission import Submission
from .document import Document
from .parser.document_parsing.sec_parser import Parser


# Set up Jupyter support only when imported
_setup_jupyter()

# reminder to setup google colab

__all__ = [
    'Downloader',
    'parse_textual_filing',
    'load_package_csv',
    'load_package_dataset',
    'Parser',
    'Filing',
    'DatasetBuilder'
]
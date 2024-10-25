# datamule/__init__.py
import sys
import nest_asyncio
from importlib.util import find_spec

def _is_jupyter():
    """Check if the code is running in a Jupyter environment."""
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter

# Apply nest_asyncio if running in Jupyter
if _is_jupyter():
    nest_asyncio.apply()

from .downloader.sec_downloader import Downloader
from .datamule_api import parse_textual_filing
from .helper import load_package_csv, load_package_dataset
from .parser.sec_parser import Parser
from .sec_filing import Filing
from .global_vars import *

# Conditionally import DatasetBuilder
if find_spec('pandas') is not None:  # Check if pandas is installed
    try:
        from .dataset_builder.dataset_builder import DatasetBuilder
    except ImportError:
        # If import fails for any other reason, DatasetBuilder won't be available
        pass

# Add DatasetBuilder to __all__ if it's available
__all__ = [
    'Downloader',
    'parse_textual_filing',
    'load_package_csv',
    'load_package_dataset',
    'Parser',
    'Filing'
]

if 'DatasetBuilder' in globals():
    __all__.append('DatasetBuilder')
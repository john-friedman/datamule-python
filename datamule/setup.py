from setuptools import setup, find_packages

from pathlib import Path
long_description = Path("../readme.md").read_text()

setup(
    name="datamule",
    author="John Friedman",
    version="0.12",
    description = "Making it easier to use SEC filings",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    url="https://github.com/john-friedman/datamule-python",
    install_requires=[
        'aiohttp',
        'aiolimiter',
        'pandas',
        'tqdm',
        'requests'
    ],
)
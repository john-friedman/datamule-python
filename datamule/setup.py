from setuptools import setup, find_packages

from pathlib import Path
long_description = Path("../readme.md").read_text()

setup(
    name="sec_parsers",
    author="John Friedman",
    version="0.549",
    description = "A package to parse SEC filings",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    url="https://github.com/john-friedman/SEC-Parsers",
    install_requires=[
        'lxml', 
        'requests',
    ],
    extras_require={
        'downloaders': ['sec_downloaders'],
        'visualizers': ['sec_visualizers'],
        'all': ['sec_downloaders', 'sec_visualizers'],
    },
)
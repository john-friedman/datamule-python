from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
from pathlib import Path
import os

# Add Windows SDK paths
sdk_include_dirs = [
    r"C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\ucrt",
    r"C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0\shared"
]

# Add Windows SDK and UCRT lib paths
sdk_lib_dirs = [
    r"C:\Program Files (x86)\Windows Kits\10\Lib\10.0.22621.0\um\x64",    # For Windows SDK libs
    r"C:\Program Files (x86)\Windows Kits\10\Lib\10.0.22621.0\ucrt\x64"   # For UCRT libs
]

# Add all existing SDK paths
include_dirs = [path for path in sdk_include_dirs if os.path.exists(path)]
library_dirs = [path for path in sdk_lib_dirs if os.path.exists(path)]

# Define Cython extension with compiler directives
extensions = [
    Extension(
        "datamule.rewrite.sgml_parser_cy",
        ["datamule/rewrite/sgml_parser_cy.pyx"],
        include_dirs=include_dirs,
        library_dirs=library_dirs,
    )
]

# Cython compiler directives
cython_directives = {
    'language_level': "3",
    'boundscheck': False,
    'wraparound': False,
    'initializedcheck': False,
    'cdivision': True,
}

long_description = Path("../readme.md").read_text(encoding='utf-8')
license_text = Path("../LICENSE").read_text(encoding='utf-8')

extras = {
    "filing_viewer": ["lxml"],
    "mulebot": ['openai'],
    "mulebot_server": ['flask'],
    "dataset_builder": ['pandas', 'google-generativeai', 'psutil']
}

all_dependencies = set(dep for extra_deps in extras.values() for dep in extra_deps)
extras["all"] = list(all_dependencies)

setup(
    name="datamule",
    author="John Friedman",
    version="0.382",
    description="Making it easier to use SEC filings.",
    long_description=long_description,
    license=license_text,
    long_description_content_type='text/markdown',
    packages=find_packages(include=['datamule*']) + ['datamule.dataset_builder'],
    url="https://github.com/john-friedman/datamule-python",
    install_requires=[
        'aiohttp',
        'aiolimiter',
        'tqdm',
        'requests',
        'nest_asyncio',
        'aiofiles',
        'polars',
        'setuptools',
        'selectolax',
        'cython'
    ],
    ext_modules=cythonize(
        extensions,
        compiler_directives=cython_directives,
        annotate=True  # Generates HTML annotation of Python interaction
    ),
    extras_require=extras,
    package_data={
        "datamule": ["data/*.csv"],
        "datamule.mulebot.mulebot_server": [
            "templates/*.html",
            "static/css/*.css",
            "static/scripts/*.js"
        ],
    },
    include_package_data=True,
)
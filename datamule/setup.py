from setuptools import setup, Extension
from pathlib import Path
import platform
import os
from setuptools import find_namespace_packages

extras = {
    "mulebot": ['openai'],
    "mulebot_server": ['flask'],
    "dataset_builder": ['txt2dataset']
}

all_dependencies = set(dep for extra_deps in extras.values() for dep in extra_deps)
extras["all"] = list(all_dependencies)

setup(
    name="datamule",
    author="John Friedman",
    version="0.5.0",
    description="Making it easier to use SEC filings.",
    packages=find_namespace_packages(include=['datamule*']),
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
        'pytz',
        'zstandard',
        'doc2dict',
        'secsgml'
    ],
    setup_requires=[
        'cython',
    ],
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
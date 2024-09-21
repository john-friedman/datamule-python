from setuptools import setup, find_packages
from pathlib import Path

long_description = Path("../readme.md").read_text()

# TODO before push
# Define the extras and their dependencies
extras = {
    "filing_viewer": ["lxml"],
    "mulebot": ['openai'],
    "mulebot_server": ['flask']
}

# Create the 'all' option
all_dependencies = set(dep for extra_deps in extras.values() for dep in extra_deps)
extras["all"] = list(all_dependencies)

setup(
    name="datamule",
    author="John Friedman",
    version="0.312",
    description="Making it easier to use SEC filings.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    url="https://github.com/john-friedman/datamule-python",
    install_requires=[
        'aiohttp',
        'aiolimiter',
        'tqdm',
        'requests',
        'nest_asyncio'
    ],
    extras_require=extras,
    package_data={
        "datamule": ["data/*.csv"],
    },
    include_package_data=True,
)
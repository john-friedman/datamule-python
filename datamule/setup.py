from setuptools import setup
from setuptools import find_namespace_packages

setup(
    name="datamule",
    author="John Friedman",
    version="1.0.6",
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
        'secsgml',
        'lxml'
    ],
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
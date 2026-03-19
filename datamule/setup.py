from setuptools import setup, find_packages

setup(
    name="datamule",
    author="John Friedman",
    version="3.6.1",
    description="Work with SEC submissions at scale.",
    packages=find_packages(include=['datamule', 'datamule.*']),
    url="https://github.com/john-friedman/datamule-python",
    install_requires=[
        'aiohttp',
        'aiolimiter',
        'tqdm',
        'requests',
        'nest_asyncio',
        'aiofiles',
        'setuptools',
        'selectolax',
        'pytz',
        'zstandard',
        'doc2dict',
        'secxbrl',
        'secsgml2',
        'websocket-client',
        'company_fundamentals',
        'flashtext',
        'aioboto3',
    ],
    package_data={
        'datamule': [
            'mapping_dicts/xml_mapping_jsons/*.json',
        ],
    },
    include_package_data=True,
)
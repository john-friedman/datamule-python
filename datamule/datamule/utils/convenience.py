from itertools import chain
from ..helper import _process_cik_and_metadata_filters, load_package_dataset
from ..utils.format_accession import format_accession

def _load_all_filer_metadata():
    """Load both listed and unlisted filer metadata as a single iterable."""
    return chain(
        load_package_dataset('listed_filer_metadata'),
        load_package_dataset('unlisted_filer_metadata')
    )

def get_ciks_from_tickers(tickers):
    return _process_cik_and_metadata_filters(ticker=tickers)

def get_tickers_from_ciks(ciks):
    if isinstance(ciks, (str, int)):
        ciks = [int(ciks)]
    else:
        ciks = [int(c) for c in ciks]
    cik_set = set(ciks)
    ticker_map = {}
    for company in _load_all_filer_metadata():
        cik = int(company['cik'])
        if cik in cik_set:
            tickers = [
                t.strip()
                for t in company['tickers'][1:-1].replace("'", "").replace('"', '').split(',')
                if t.strip()
            ]
            ticker_map[cik] = tickers[0] if tickers else ''
    return [ticker_map.get(cik, '') for cik in ciks]

def get_company_names_from_ciks(ciks):
    if isinstance(ciks, (str, int)):
        ciks = [int(ciks)]
    else:
        ciks = [int(c) for c in ciks]
    cik_set = set(ciks)
    name_map = {int(c['cik']): c['name'] for c in _load_all_filer_metadata() if int(c['cik']) in cik_set}
    return [name_map.get(cik, '') for cik in ciks]

def get_sics_from_ciks(ciks):
    if isinstance(ciks, (str, int)):
        ciks = [int(ciks)]
    else:
        ciks = [int(c) for c in ciks]
    cik_set = set(ciks)
    sic_map = {int(c['cik']): c['sic'] for c in _load_all_filer_metadata() if int(c['cik']) in cik_set}
    return [sic_map.get(cik, '') for cik in ciks]

def get_adm0_from_ciks(ciks):
    if isinstance(ciks, (str, int)):
        ciks = [int(ciks)]
    else:
        ciks = [int(c) for c in ciks]
    cik_set = set(ciks)
    adm0_map = {}
    for c in _load_all_filer_metadata():
        cik = int(c['cik'])
        if cik in cik_set:
            desc = c['business_stateOrCountryDescription']
            adm0_map[cik] = 'United States of America' if len(desc) == 2 else desc
    return [adm0_map.get(cik, '') for cik in ciks]


def get_us_state_from_ciks(ciks):
    if isinstance(ciks, (str, int)):
        ciks = [int(ciks)]
    else:
        ciks = [int(c) for c in ciks]
    cik_set = set(ciks)
    state_map = {}
    for c in _load_all_filer_metadata():
        cik = int(c['cik'])
        if cik in cik_set:
            desc = c['business_stateOrCountryDescription']
            state_map[cik] = desc if len(desc) == 2 else ''
    return [state_map.get(cik, '') for cik in ciks]

def get_us_zipcodes_from_ciks(ciks):
    if isinstance(ciks, (str, int)):
        ciks = [int(ciks)]
    else:
        ciks = [int(c) for c in ciks]
    cik_set = set(ciks)
    zip_map = {}
    for c in _load_all_filer_metadata():
        cik = int(c['cik'])
        if cik in cik_set:
            desc = c['business_stateOrCountryDescription']
            zip_map[cik] = c['business_zipCode'] if len(desc) == 2 else None
    return [zip_map.get(cik, None) for cik in ciks]

def get_business_street1_from_ciks(ciks):
    if isinstance(ciks, (str, int)):
        ciks = [int(ciks)]
    else:
        ciks = [int(c) for c in ciks]
    cik_set = set(ciks)
    street_map = {int(c['cik']): c['business_street1'] for c in _load_all_filer_metadata() if int(c['cik']) in cik_set}
    return [street_map.get(cik, '') for cik in ciks]


# URL constructors
def construct_index_url(accession):
    return f"https://www.sec.gov/Archives/edgar/data/{format_accession(accession,'no-dash')}/{format_accession(accession,'dash')}-index.html"

def construct_sgml_url(accession, cik):
    return f"https://www.sec.gov/Archives/edgar/data/{str(int(cik))}/{format_accession(accession,'no-dash')}/{format_accession(accession,'dash')}.txt"

def construct_folder_url(accession, cik):
    return f"https://www.sec.gov/Archives/edgar/data/{str(int(cik))}/{format_accession(accession,'no-dash')}/"

def construct_document_url(accession, cik, filename):
    return f"https://www.sec.gov/Archives/edgar/data/{str(int(cik))}/{format_accession(accession,'no-dash')}/{filename}"
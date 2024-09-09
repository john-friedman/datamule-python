import requests
# this will be deprecated in the future. Turns out using accession number saves space.
def construct_primary_doc_url(cik,filing_entity,accepted_year,filing_count,primary_doc_url):
    base_url = 'https://www.sec.gov/Archives/edgar/data'
    accession_number = f'{str(filing_entity).zfill(10)}{str(accepted_year).zfill(2)}{str(filing_count).zfill(6)}'
    return f'{base_url}/{cik}/{accession_number}/{primary_doc_url}'

def construct_primary_doc_url_from_cik_and_accession_number(cik, accession_number,primary_doc_url):
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{primary_doc_url}"

def query_datamule_api(**kwargs):
    base_url = "https://api.datamule.xyz/submissions"
    
    # Convert date_range and filing_date to comma-separated strings if they're lists or tuples
    for key in ['date_range', 'filing_date']:
        if key in kwargs and isinstance(kwargs[key], (list, tuple)):
            kwargs[key] = ','.join(kwargs[key])
    
    response = requests.get(base_url, params=kwargs)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()
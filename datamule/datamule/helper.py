
def construct_primary_doc_url(cik,filing_entity,accepted_year,filing_count,primary_doc_url):
    base_url = 'https://www.sec.gov/Archives/edgar/data/'
    accession_number = f'{filing_entity.zfill(10)}-{accepted_year.zfill(2)}-{filing_count.zfill(18)}'

    return f'{base_url}/{cik}/{accession_number}/{primary_doc_url}'

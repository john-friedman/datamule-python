from ..helper import _process_cik_and_metadata_filters
from ..utils.format_accession import format_accession

def get_ciks_from_tickers(tickers):
    return _process_cik_and_metadata_filters(ticker=tickers)

def construct_index_url(accession):
    return f"https://www.sec.gov/Archives/edgar/data/{format_accession(accession,'no-dash')}/{format_accession(accession,'dash')}-index.html"

def construct_sgml_url(accession,cik):
    return f"https://www.sec.gov/Archives/edgar/data/{str(int(cik))}/{format_accession(accession,'no-dash')}/{format_accession(accession,'dash')}.txt"

def construct_folder_url(accession,cik):
    return f"https://www.sec.gov/Archives/edgar/data/{str(int(cik))}/{format_accession(accession,'no-dash')}/"

def construct_document_url(accession,cik,filename):
    return f"https://www.sec.gov/Archives/edgar/data/{str(int(cik))}/{format_accession(accession,'no-dash')}/{filename}"

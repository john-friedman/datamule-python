from ..helper import _process_cik_and_metadata_filters

def get_ciks_from_tickers(tickers):
    return _process_cik_and_metadata_filters(ticker=tickers)
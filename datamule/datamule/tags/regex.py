# Exchange ticker regexes with word boundaries
nyse_regex = r"\b([A-Z]{1,4})(\.[A-Z]+)?\b"
nasdaq_regex = r"\b([A-Z]{1,5})(\.[A-Z]+)?\b"
nyse_american_regex = r"\b([A-Z]{1,5})(\.[A-Z]+)?\b"
london_stock_exchange_regex = r"\b([A-Z]{3,4})(\.[A-Z]+)?\b"
toronto_stock_exchange_regex = r"\b([A-Z]{1,5})(\.[A-Z]+)?\b"
euronext_paris_regex = r"\b([A-Z]{2,12})(\.[A-Z]+)?\b"
euronext_amsterdam_regex = r"\b([A-Z]{1,5})(\.[A-Z]+)?\b"
euronext_brussels_regex = r"\b([A-Z]{1,5})(\.[A-Z]+)?\b"
euronext_lisbon_regex = r"\b([A-Z]{3,5})(\.[A-Z]+)?\b"
euronext_milan_regex = r"\b([A-Z]{2,5})(\.[A-Z]+)?\b"
deutsche_borse_xetra_regex = r"\b([A-Z0-9]{3,6})(\.[A-Z]+)?\b"
six_swiss_exchange_regex = r"\b([A-Z]{2,6})(\.[A-Z]+)?\b"
tokyo_stock_exchange_regex = r"\b(\d{4})\b"
hong_kong_stock_exchange_regex = r"\b(\d{4,5})\b"
shanghai_stock_exchange_regex = r"\b(6\d{5})\b"
shenzhen_stock_exchange_regex = r"\b([03]\d{5})\b"
australian_securities_exchange_regex = r"\b([A-Z]{3})(\.[A-Z]+)?\b"
singapore_exchange_regex = r"\b([A-Z]\d{2}[A-Z]?)(\.[A-Z]+)?\b"
nse_bse_regex = r"\b([A-Z&]{1,10})(\.[A-Z]+)?\b"
sao_paulo_b3_regex = r"\b([A-Z]{4}\d{1,2})(\.[A-Z]+)?\b"
mexico_bmv_regex = r"\b([A-Z*]{1,7})(\.[A-Z]+)?\b"
korea_exchange_regex = r"\b(\d{6})\b"
taiwan_stock_exchange_regex = r"\b(\d{4})\b"
johannesburg_stock_exchange_regex = r"\b([A-Z]{3})(\.[A-Z]+)?\b"
tel_aviv_stock_exchange_regex = r"\b([A-Z]{4})(\.[A-Z]+)?\b"
moscow_exchange_regex = r"\b([A-Z]{4})(\.[A-Z]+)?\b"
istanbul_stock_exchange_regex = r"\b([A-Z]{5})(\.[A-Z]+)?\b"
nasdaq_stockholm_regex = r"\b([A-Z]{3,4})( [A-Z])?(\.[A-Z]+)?\b"
oslo_bors_regex = r"\b([A-Z]{3,5})(\.[A-Z]+)?\b"
otc_markets_us_regex = r"\b([A-Z]{4,5})[FY]?(\.[A-Z]+)?\b"
pink_sheets_regex = r"\b([A-Z]{4,5})(\.[A-Z]+)?\b"

ticker_regex_list = [
    ("nyse", r"\b([A-Z]{1,4})(\.[A-Z]+)?\b"),
    ("nasdaq", r"\b([A-Z]{1,5})(\.[A-Z]+)?\b"),
    ("nyse_american", r"\b([A-Z]{1,5})(\.[A-Z]+)?\b"),
    ("london_stock_exchange", r"\b([A-Z]{3,4})(\.[A-Z]+)?\b"),
    ("toronto_stock_exchange", r"\b([A-Z]{1,5})(\.[A-Z]+)?\b"),
    ("euronext_paris", r"\b([A-Z]{2,12})(\.[A-Z]+)?\b"),
    ("euronext_amsterdam", r"\b([A-Z]{1,5})(\.[A-Z]+)?\b"),
    ("euronext_brussels", r"\b([A-Z]{1,5})(\.[A-Z]+)?\b"),
    ("euronext_lisbon", r"\b([A-Z]{3,5})(\.[A-Z]+)?\b"),
    ("euronext_milan", r"\b([A-Z]{2,5})(\.[A-Z]+)?\b"),
    ("deutsche_borse_xetra", r"\b([A-Z0-9]{3,6})(\.[A-Z]+)?\b"),
    ("six_swiss_exchange", r"\b([A-Z]{2,6})(\.[A-Z]+)?\b"),
    ("tokyo_stock_exchange", r"\b(\d{4})\b"),
    ("hong_kong_stock_exchange", r"\b(\d{4,5})\b"),
    ("shanghai_stock_exchange", r"\b(6\d{5})\b"),
    ("shenzhen_stock_exchange", r"\b([03]\d{5})\b"),
    ("australian_securities_exchange", r"\b([A-Z]{3})(\.[A-Z]+)?\b"),
    ("singapore_exchange", r"\b([A-Z]\d{2}[A-Z]?)(\.[A-Z]+)?\b"),
    ("nse_bse", r"\b([A-Z&]{1,10})(\.[A-Z]+)?\b"),
    ("sao_paulo_b3", r"\b([A-Z]{4}\d{1,2})(\.[A-Z]+)?\b"),
    ("mexico_bmv", r"\b([A-Z*]{1,7})(\.[A-Z]+)?\b"),
    ("korea_exchange", r"\b(\d{6})\b"),
    ("taiwan_stock_exchange", r"\b(\d{4})\b"),
    ("johannesburg_stock_exchange", r"\b([A-Z]{3})(\.[A-Z]+)?\b"),
    ("tel_aviv_stock_exchange", r"\b([A-Z]{4})(\.[A-Z]+)?\b"),
    ("moscow_exchange", r"\b([A-Z]{4})(\.[A-Z]+)?\b"),
    ("istanbul_stock_exchange", r"\b([A-Z]{5})(\.[A-Z]+)?\b"),
    ("nasdaq_stockholm", r"\b([A-Z]{3,4})( [A-Z])?(\.[A-Z]+)?\b"),
    ("oslo_bors", r"\b([A-Z]{3,5})(\.[A-Z]+)?\b"),
    ("otc_markets_us", r"\b([A-Z]{4,5})[FY]?(\.[A-Z]+)?\b"),
    ("pink_sheets", r"\b([A-Z]{4,5})(\.[A-Z]+)?\b"),
]  
# Security identifier regexes with word boundaries
cusip_regex = r"\b[0-9A-Z]{8}[0-9]\b"
isin_regex = r"\b[A-Z]{2}[0-9A-Z]{9}[0-9]\b"
figi_regex = r"\b[A-Z]{2}G[A-Z0-9]{8}[0-9]\b"

particles = {
   # Dutch - single words only
   'van', 'der', 'den', 'de',
   
   # German - single words only  
   'von', 'zu', 'vom', 'zur', 'zum',
   
   # Spanish - single words only
   'de', 'del', 'y',
   
   # Portuguese - single words only
   'da', 'das', 'do', 'dos', 'e',
   
   # French - single words only
   'de', 'du', 'des', 'le', 'la', 'les', "d'",
   
   # Italian - single words only
   'da', 'di', 'del', 'della', 'delle', 'dei', 'degli', 'dello',
   
   # Irish/Scottish
   'mac', 'mc', 'o',
   
   # Arabic
   'al', 'el', 'ibn', 'bin', 'bint', 'abu',
   
   # Other European
   'af', 'av',  # Scandinavian
   'ter',       # Dutch/Flemish
   'op',        # Dutch
   'aan',       # Dutch
   'ten',       # Dutch
   'het',       # Dutch
   'in',        # Dutch
}
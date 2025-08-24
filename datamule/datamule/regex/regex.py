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
   nyse_regex,
   nasdaq_regex,
   nyse_american_regex,
   london_stock_exchange_regex,
   toronto_stock_exchange_regex,
   euronext_paris_regex,
   euronext_amsterdam_regex,
   euronext_brussels_regex,
   euronext_lisbon_regex,
   euronext_milan_regex,
   deutsche_borse_xetra_regex,
   six_swiss_exchange_regex,
   tokyo_stock_exchange_regex,
   hong_kong_stock_exchange_regex,
   shanghai_stock_exchange_regex,
   shenzhen_stock_exchange_regex,
   australian_securities_exchange_regex,
   singapore_exchange_regex,
   nse_bse_regex,
   sao_paulo_b3_regex,
   mexico_bmv_regex,
   korea_exchange_regex,
   taiwan_stock_exchange_regex,
   johannesburg_stock_exchange_regex,
   tel_aviv_stock_exchange_regex,
   moscow_exchange_regex,
   istanbul_stock_exchange_regex,
   nasdaq_stockholm_regex,
   oslo_bors_regex,
   otc_markets_us_regex,
   pink_sheets_regex,
]

# Security identifier regexes with word boundaries
cusip_regex = r"\b[0-9A-Z]{8}[0-9]\b"
isin_regex = r"\b[A-Z]{2}[0-9A-Z]{9}[0-9]\b"
figi_regex = r"\b[A-Z0-9]{12}\b"
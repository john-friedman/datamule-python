start
1. Get url
2. get d['hits']['total']['value']
3. If more than 10,000 calculate 


def find_api_urls: single thread
1. start 
2. get d['hits']['total']['value']
3. if more than 10,000 subset by date
4. if more than 10,000 left for specific date remove forms until fits, saves to grab later
5. if good, sends to get_indices_from_api


def get_indices_from_api():
* given query with less than 10,000 hits
* we just need primary doc url, cik, acc_no
* construct full url
return

def download_urls()
* already written


how it works
find_api_urls finds urls batches
sends to get indices which returns filing primary doc urls
sends to def download urls which downloads them



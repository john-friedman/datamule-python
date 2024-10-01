# Downloader

Uses EFTS to find filings, and SEC endpoint to download them. The SEC *officially* allows 10 requests / second. In practice, that is not the case.

## Current Problems:
* Downloader fails on large downloads (e.g. > 10k)

## Filings different location on EFTS than SEC.gov
* e.g. a file ending with 0001.txt will really have filename {accession number with dashes}-0001.txt
* some other stuff like this. Will inspect metadata for analysis later.

## Notes
* Switching wifi will reset rate limits
* not sure if I'm hit with more rate limits because unusual activity or because change in approach.
* will try different wifi and poss different machine
* there is some weird voodo happening. Sometimes rate limit comes back and then it processes like normal.
* will see how multithreading approach holds up in morning. 

# New approach
rate limit triggers 3601 second backoff?
warning if hit rate limit (to set around 5)
async + switch sessions on 429
add jitter. make sure jitter does not exceed cap
add option to not download existing
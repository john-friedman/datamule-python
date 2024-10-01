### SEC.gov

The SEC website has a lot of endpoints
* submission endpoints
* company facts endpoints
* company concept endpoints
* XBRL Frames endpoint

It also has interesting data in the archives:
* filing endpoints e.g. https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.htm


### Filing Endpoint



#### Downloads

## Rate Limits
* The official SEC rate limit is 10 requests / second. In practice, the rate limit is less than 10 requests / second, and they will block your session within 5-20 minutes.
* If you create a new session, the rate limit is often lifted.
* I'm not sure why this is. Maybe there is an rate limit per ten minutes that is unlisted.

## Solution
* 9 requests / second
* Whenever 429 is returned, switch to a new session
* Add 1 second to delay to EFTS during handover.
* This seems to work. Currently testing on alternative script. Will rework downloader, test on 8-K batch.

Note: a lot of the code is AI slop to test new concepts out.

Ok new approach. I think SEC is a lil frustrated with me. So I should let them cool off. However.
Going to try multithreading instead of async because async has some weird stuff.
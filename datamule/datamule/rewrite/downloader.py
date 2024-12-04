from aiolimiter import AsyncLimiter

# Note: We are removing some functionality temporarily from the original Downloader class such as filter by sics.
# if people complain, we will add it back sooner
# main reason is to simplify / add additional features to the class that are more important.
class Downloader:
    def __init__(self):
        self.headers = {'User-Agent': 'First Last firstlast@gmail.com'}
        self.domain_limiters = {
            'www.sec.gov': AsyncLimiter(10, 1),
            'efts.sec.gov': AsyncLimiter(10, 1),
            'data.sec.gov': AsyncLimiter(10, 1),
            'default': AsyncLimiter(10, 1),
            'library.datamule.xyz': AsyncLimiter(1000, 1),
        }

    def set_headers(self, user_agent):
        self.headers = {'User-Agent': user_agent}

    def set_limiter(self, domain, rate_limit):
        self.domain_limiters[domain] = AsyncLimiter(rate_limit, 1)

    def download(self, output_dir='filings', cik=None, ticker=None, submission_type=None, document_type=None,
                date=None):
        """"""
        pass


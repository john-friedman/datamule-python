from sec_downloader import Downloader


downloader = Downloader(rate_limit=10)

downloader.download(form='10-K',cik='1318605')


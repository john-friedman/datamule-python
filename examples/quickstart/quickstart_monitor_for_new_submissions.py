from datamule import Portfolio

portfolio = Portfolio('monitor')
# monitoring
def print_hits(hits):
    print(hits)

# polling the sec
portfolio.monitor_submissions(data_callback=print_hits, interval_callback=None,
                            polling_interval=1000, quiet=False, start_date=None,
                            validation_interval=60000)

# streaming using datamule's websocket
portfolio.stream_submissions(data_callback=print_hits,quiet=False)

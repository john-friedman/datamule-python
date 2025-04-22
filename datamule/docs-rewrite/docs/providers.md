# Providers

<b>datamule</b> supports multiple data providers.

## SEC
* Rate limited (5/s)

## datamule
* No rate limits
* Convenience fee

### Pricing
* $1 / 100,000 SEC Archive downloads - will try to lower this to $.01 in the future.
* $60 / tb queried for SEC Data Warehouse (e.g. Sheet()) - this is 10x the BigQuery cost of provision.

## Self-hosting

### Bootstrap Guides
The data provided by <b>datamule</b> can be self hosted. Here are some rough guides.

1. [Putting Institutional Holdings in a Data Warehouse](https://medium.com/@jgfriedman99/putting-institutional-holdings-in-a-data-warehouse-eadb1b4d2661)
2. [How to host the SEC Archive for $20/month](https://medium.com/@jgfriedman99/how-to-host-the-sec-archive-for-20-month-da374cc3c3fb)

### Bringing the data into your own cloud

If you want to ingest data into your own infrastructure (e.g. Snowflake), feel free to [contact me](johnfriedman@datamule.xyz). 


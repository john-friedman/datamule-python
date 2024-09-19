https://www.sec.gov/search-filings/edgar-application-programming-interfaces


data.sec.gov/api/xbrl/companyfacts/ - return all concepts for a company

data.sec.gov/api/xbrl/frames/ - aggregates one fact for all companies that most clearly fit period
supports for annual, quarterly and instantaneous data:

* will need to request for each of these and create csv of which company has what
* think about code reusabilty - probably worth refactoring datamule a bit
* save this for later
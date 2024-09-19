https://www.sec.gov/search-filings/edgar-application-programming-interfaces

data.sec.gov/submissions/

This JSON data structure contains metadata such as current name, former name, and stock exchanges and ticker symbols of publicly-traded companies. The object’s property path contains at least one year’s of filing or to 1,000 (whichever is more) of the most recent filings in a compact columnar data array. If the entity has additional filings, files will contain an array of additional JSON files and the date range for the filings each one contains. Contains primary doc url, which is nice.

data.sec.gov/api/xbrl/companyfacts/ - return all concepts for a company

data.sec.gov/api/xbrl/companyconcept/ - returns a specific concept for a company - won't use because company facts has all the data.

data.sec.gov/api/xbrl/frames/ - aggregates one fact for all companies that most clearly fit period
supports for annual, quarterly and instantaneous data:

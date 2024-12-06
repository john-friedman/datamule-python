# Bulk Downloads

Currently using DropBox and Zenodo. 

Zenodo:
* 50 gb per record, with up to 100 files
* Official rate limit of 60 requests/ second
* Download speed of 1-4mb/s, making partitions necessary
* Looks like we can use the API to setup a pipeline that downloads the data from SEC, partitions it, stores info in package metadata, and uploads to zenodo. This might be a good solution as we can theoretically get 120mb/s transfer from Zenodo with partitions.

DropBox
* 2gb free tier
* Download speed of 8-15 mb/s
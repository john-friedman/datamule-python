Book
====

Book is a class that allows you to download and process tabular datasets.

Functions
---------

``process_dataset(dataset_name, typical args)``
    Retrieves the data and processes it. Does not save the data to disk, but will use saved data if available.


``download_dataset(dataset_name, typical args)``
    Retrieves the data and saves it to disk.
    

Datasets
--------
* XBRL (via sec, free)
* 345 (via datamule, paid)
* 13F-HR (via datamule, paid)

..note ::
    xbrl uses frames endpoint or companyfacts endpoint
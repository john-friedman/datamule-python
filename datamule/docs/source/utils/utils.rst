Utils
=====

RSS Submissions Monitor
-----------------------

Monitors RSS for new submissions.

EFTSQuery
---------

Monitors efts for new submissions. Splits queries into chunks to avoid max query length.

EFTS Monitor
------------


Monitor
-------

Uses EFTS Monitor for backfill, and RSS Monitor for new submissions.

TextSearch
----------

Finds SEC Submissions which contain a given text.

Submissions Streamer
--------------------

Streams SEC Submissions.

Note:
name: Name of the company. Uses autocomplete to find the company. E.g. 'Apple Inc' will return Apple as well as Apple iSports Group, Inc. (AAPI), etc.
location: Location of the Principal Executive Offices (e.g. "CA", "X0") Note: "X0" is United Kingdom

are available for some of these. Has not been integrated into the main package yet.


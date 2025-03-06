Portfolio
=========

Functions
---------

``process_submissions(typical args)``
   Retrieves the submissions and processes them. Does not save the data to disk, but will use saved submissions if available.

``download_submissions(typical args)``
   Retrieves the submissions and saves them to disk.

``filter_text(query)``
   filters submissions by text.

``filter_xbrl(logic)
   filters submissions by xbrl logic.

``monitor_submissions(typical args)``
   Monitors for new submissions.

Submission
----------

Submissions are the core of the Portfolio class.

submission.metadata

Document
--------

Documents are the core of the Submission class.

document.parse()
document.load()

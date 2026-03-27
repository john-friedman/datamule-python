# Get Friday Night Dump

Get 8-K's filed after 4pm ET. See: [Friday Night Dump](https://www.linkedin.com/posts/michelle-leder-341aa8_fridaynightdump-ugcPost-7232824150883512320-ysbN?utm_source=share&utm_medium=member_desktop&rcm=ACoAADDUGJEBEAnHUqaSouOFt49MMUOHBP0evwk).

```python
from datamule import Sheet
from datetime import datetime
from zoneinfo import ZoneInfo

# Set your times in ET
start_et = datetime(2026, 3, 27, 16, 0, 0, tzinfo=ZoneInfo("America/New_York"))
end_et = datetime(2026, 3, 27, 23, 59, 59, tzinfo=ZoneInfo("America/New_York"))

# Convert to UTC strings for the API
start_utc = start_et.astimezone(ZoneInfo("UTC")).strftime('%Y-%m-%d %H:%M:%S')
end_utc = end_et.astimezone(ZoneInfo("UTC")).strftime('%Y-%m-%d %H:%M:%S')

sheet = Sheet('')

result = sheet.get_table('sec-filings-lookup',
    submissionType='8-K',
    filingDate='2026-03-27',
    detectedTime=(start_utc, end_utc))

print(len(result))
```
Result
```
110
```

`get_ciks_from_tickers`

```
from datamule.utils.convenience import get_ciks_from_tickers
print(get_ciks_from_tickers(['IBM']))
```
```
[51143]
```

```
from datamule.utils.convenience import get_ciks_from_tickers
print(get_ciks_from_tickers(['TSLA','IBM']))
```
```
[1318605, 51143]
```
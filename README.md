# Free Proxy

Simple free proxy scraper and validator

## Installation
```bash
pip install git+https://${GITHUB_TOKEN}@github.com/ajanderson1/espc-scraper -vvv
```

## Usage:
```python
from free_proxy import *
```

### Get full proxy list
```python
proxy_list()
```

### Get a list of filtered proxies
```python
filtered_proxy_list({
    'code':'GB', 
    'https`:'yes'
    })
```

### Normal Usage: get first valid proxy satisfying a filter
This returns the first valid proxy that is found (by random) in fromat {ip:port}
```python
get_first_valid_proxy(
    filtered_proxy_list({
        'code':'US', 
        'https':'yes'
        })
)
```



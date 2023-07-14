# Free Proxy

Retrieves and filters free proxies from https://free-proxy-list.net/
Optional filter by: `ip`, `port`, `code`, `country`, `anonymity`, `google`, `https`, `last_checked`

## Installation
```bash
export GITHUB_TOKEN=your_github_token
pip install git+https://${GITHUB_TOKEN}@github.com/ajanderson1/free_proxy -vvv
```

## Usage:

Import using:
```python
from free_proxy import get_first_operational_proxy, get_all_operational_proxies, test_proxy
```


### Get first operational proxy (matching optional filters)
```python
# Returns the first valid proxy that is found (by random), in fromat "ip:port"
get_first_operational_proxy(filter_by={
    'code':'my_code', 
    'country':'my_country', 
    'anonymity':'elite XXXX',
    })
```

### Get All operational proxies (matching optional filters)
```python
# Returns a list of all valid proxies found, in format "ip:port"
get_all_operational_proxies(filter_by={
    'code':'my_code', 
    'country':'my_country', 
    'anonymity':'elite XXXX',
    })
```


### Test proxy
```python
# Returns True if proxy is valid, False otherwise
test_proxy({
    'ip':'my_ip', 
    'port':'my_port'
    })
```
or 
```python
test_proxy('my_ip:my_port')
``` 

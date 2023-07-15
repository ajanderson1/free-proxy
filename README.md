# free-proxy

---

## Proxy List Manager

The Proxy List Manager allows you to download, filter, and validate proxies from different sources. It uses a mixture of `BeautifulSoup` to scrape proxies from *'free-proxy-list.net'* and `requests` to download from '`[SpeedX/PROXY-List](https://github.com/TheSpeedX/PROXY-List).  It then includes functionality to check if the proxies are still operational and return the first *'n'* operational proxy.

## Installation

`free_proxy` requires dependencies: `beautifulsoup4` and `requests`. You can install these by running:

```sh
pip install beautifulsoup4 requests
```

To install `free_proxy` using pip:
```sh
pip install git+https://github.com/ajanderson1/free_proxy.git
```


## Usage

```python
from free_proxy import ProxyListManager
```

Here is a basic usage example:

```python
# create a proxy list from the source 'free-proxy-list.net'
proxy_list = ProxyListManager() # retrieve proxies from SpeedX/PROXY-List
# ...or...
proxy_list = ProxyListManager(source='free-proxy-list.net') # retrieve proxies from free-proxy-list.net

# Find the first operational proxy from the filtered list
first_operational_proxy = proxy_list.get_first_operational_proxy()

# Or, find the first three operational proxies from the filtered list
three_operational_proxies = proxy_list.return_n_operational_proxies(n=3, filter_by={'code': 'US'})  #NB filter by 'country code' only works for free-proxy-list.net proxies.  Error messages give more details.
```

Please note that `return_first_operational_proxy` and `return_n_operational_proxies` functions may take some time to run, as they test each proxy in turn. The functions will stop as soon as they find a proxy or n proxies that are operational.

## Testing

Tests are written using the pytest library. To run the tests, install pytest using pip:

```sh
pip install pytest
```

Then, run the tests with:

```sh
pytest test_free_proxy.py  # replace 'test_your_module.py' with the name of your test file
```

## Responsible Proxy Use

When using the Proxy List Manager, ensure your use of proxies is legal and respectful of the websites you're accessing. Do not use proxies for unauthorized access, data scraping, or spam.
# free-proxy

---

## Proxy List Manager

The Proxy List Manager allows you to download, filter, and validate proxies from different sources. It uses a mixture of `BeautifulSoup` to scrape proxies from *'free-proxy-list.net'* and `requests` to download from '`[SpeedX/PROXY-List](https://github.com/TheSpeedX/PROXY-List).  It then includes functionality to check if the proxies are still operational and return the first *'n'* operational proxy.

## Installation

To install the dependencies for this project, you will need to use pip. The required dependencies are `beautifulsoup4` and `requests`. You can install these by running:

```sh
pip install beautifulsoup4 requests
```

Then, clone the repository and import the module in your Python script:

```python
import free_proxy  # replace 'your_module' with the name of your module
```

## Usage

Here is a basic usage example:

```python
# create a proxy list from the source 'free-proxy-list.net'
proxy_list = ProxyListManager(source='free-proxy-list.net')

# Now, say you want to filter proxies that are from the US
filtered_proxies = proxy_list.filter_proxies(filter_by={'country': 'US'})

# Now, you want to check if these proxies are operational
# find the first operational proxy from the filtered list
first_operational_proxy = proxy_list.return_first_operational_proxy()

# Or, find the first three operational proxies from the filtered list
three_operational_proxies = proxy_list.return_n_operational_proxies(n=3)
```

Please note that `return_first_operational_proxy` and `return_n_operational_proxies` functions may take some time to run, as they test each proxy in turn. The functions will stop as soon as they find a proxy or n proxies that are operational.

## Testing

Tests are written using the pytest library. To run the tests, install pytest using pip:

```sh
pip install pytest
```

Then, run the tests with:

```sh
pytest test_your_module.py  # replace 'test_your_module.py' with the name of your test file
```

## Responsible Proxy Use

When using the Proxy List Manager, ensure your use of proxies is legal and respectful of the websites you're accessing. Do not use proxies for unauthorized access, data scraping, or spam. Misuse may lead to legal consequences. Always respect others' rights and privacy.
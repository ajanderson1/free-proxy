from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException

import random

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


FREE_PROXY_LIST_URL = "https://free-proxy-list.net"
FREE_PROXY_LIST_URL_UK = "https://free-proxy-list.net/uk-proxy.html"

PROXY_VALIDATION_URL = "https://www.google.com"
PROXY_VALIDATION_TIMEOUT = 5

def get_proxy_list() -> list:
    """  Returns a dict of proxies scraped from web (https://free-proxy-list.net) """
    
    headers: dict = {
        'Cache-Control': 'no-cache',
        "Pragma": "no-cache"
    }
    r = requests.get(FREE_PROXY_LIST_URL, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    table = soup.find('table', {'class': 'table table-striped table-bordered'})
    proxy_list = []
    for row in table.tbody.findAll('tr'):
        proxy_single_result = {}
        proxy_single_result['ip'] = row.find_all('td')[0].text
        proxy_single_result['port'] = row.find_all('td')[1].text
        proxy_single_result['code'] = row.find_all('td')[2].text
        proxy_single_result['country'] = row.find_all('td')[3].text
        proxy_single_result['anonymity'] = row.find_all('td')[4].text
        proxy_single_result['google'] = row.find_all('td')[5].text
        proxy_single_result['https'] = row.find_all('td')[6].text
        proxy_single_result['last_checked'] = row.find_all('td')[7].text
        proxy_list.append(proxy_single_result)
    log.debug(f"Retrieved {len(proxy_list)} proxies from web")
    return proxy_list


def _filter_proxy_list(
                    proxy_list: list,
                    filter_by: dict = None
                    )-> list:
    """ 
    Retrieves and filters free proxies (based on: ip, port, code, country, anonymity, google, https, last_checked)
    Params:
        -   proxy_list (OPTIONAL): list of proxies to filter (if None, will retrieve from web)
    Returns:
        -   list of dicts in format: [{'ip': 'port', 'ip': 'port'}, ...]
            (or [], if filter matches no proxies.)

    """        
    _validate_proxy_list(proxy_list)

    if filter_by:
        # Validate that `filter_by` is a dict
        if not isinstance(filter_by, dict):
            raise TypeError("`filter_by` must be a dict")
        # Validate that all keys in `filter_by` are present in first item of `proxy_list` (already established that all keys are uniform)
        if not all([k in proxy_list[0] for k in filter_by]):
            invalid_keys = [k for k in filter_by if k not in proxy_list[0]]
            raise TypeError(f"`filter_by` contains invalid keys: {invalid_keys}.  All `filter_by` keys must be in the `proxy_list`, valid options are: {list(proxy_list[0].keys())}")
        
        filter_func = lambda proxy: [proxy[filter_k] == filter_v for filter_k, filter_v in filter_by.items()]
        results = [proxy for proxy in proxy_list if all(filter_func(proxy))] if filter_by else [{proxy['ip']: proxy['port']} for proxy in proxy_list]
        if not results:
            log.warning(f"Filtering by: {filter_by} returned no results, returning empty list")
    else:
        log.warning("No `filter_by` argument passed in. Returning all proxies.")
        results = proxy_list
        
    return results


def _validate_proxy_list(proxy_list: list) -> list:
    """ 
    Validates a list of proxies. Raises TypeError if invalid.
    Params:
        -   proxy_list (list): list of proxies to validate
    Exceptions, raises:
        -   TypeError: if `proxy_list` is passed in and not a list of dicts
        -   TypeError: if `proxy_list` is passed in and each item is not a dict
        -   TypeError: if `proxy_list` is passed in and each item contains invalid keys
        -   TypeError: if `proxy_list` is passed in and each item does not contain the keys 'ip' and 'port'

    """

    MANDATORY_KEYS = ['ip', 'port']

    # Validate the proxy is a list
    if not isinstance(proxy_list, list):
        raise TypeError("`proxy_list` must be a list")

    # Validate that each item in the list is a dict
    if not all([isinstance(proxy, dict) for proxy in proxy_list]):
        raise TypeError("`proxy_list` must be a list of dicts")
    
    # Validate that each item contains the same keys
    if not all([all([k in proxy for k in proxy_list[0]]) for proxy in proxy_list]):
        raise TypeError("`proxy_list` contains invalid keys.  Every item in list must contain uniform keys")
    
    # Validate that each item contains has the keys 'ip' and 'port'
    if not all([all([k in proxy for k in MANDATORY_KEYS]) for proxy in proxy_list]):
        raise TypeError(f"`proxy_list` must contain keys: {MANDATORY_KEYS}(at a minimum) for each item.")



def _format_proxy_as_str(proxy: dict) -> dict:
    """ Formats a proxy to the format: 'ip':'port' (e.g. '207.180.250.238:80')"""
    # Validate that proxy is a dict and contains the keys 'ip' and 'port'
    if not isinstance(proxy, dict):
        raise TypeError("`proxy` must be a dict")
    if not all([k in proxy for k in ['ip', 'port']]):
        raise TypeError("`proxy` must contain the keys 'ip' and 'port'")
    
    return f"{proxy['ip']}:{proxy['port']}"


def _format_proxy_as_dict(proxy: str) -> dict:
    """ Formats a proxy to the format: {'ip':'port'} (e.g. 
    """
    # Validate that proxy is a string and contains the keys 'ip' and 'port'
    if not isinstance(proxy, str):
        raise TypeError("`proxy` must be a string") 
    return {'ip': proxy.strip().replace(' ','').split(':')[0], 'port': proxy.replace(' ','').split(':')[1]}


def check_proxy(proxy: dict | str) -> bool:
    """ Returns True if proxy is valid, False if not """
    if isinstance(proxy, dict):
        proxy = _format_proxy_as_str(proxy)
    elif isinstance(proxy, str):
        pass
    else:
        raise TypeError("`proxy` must be a dict or string")

    try:
        log.debug(f"Testing proxy: {proxy}")
        response = requests.get(PROXY_VALIDATION_URL, proxies={"http": proxy, "https": proxy}, timeout=PROXY_VALIDATION_TIMEOUT)
        if response.status_code != 200:
            raise RequestException(f"Status Code: {response.status_code}") 
        log.info(f"Proxy: {proxy} is valid (status_code: {response.status_code}))")
        return True
    except Exception as e:
        log.error(f"Proxy: {proxy} is invalid - Exception: {e.__class__.__name__}")
        return False


def get_all_operational_proxies(
                    filter_by:dict=None, 
                    proxy_list:list=None
                    ) -> dict:
    """ Returns all valid proxies from the list of passed in proxies """
    if not proxy_list:
        proxy_list = get_proxy_list()
    else:
        log.warning("Using custom proxy list, this is not recommended.")
    
    proxies = _filter_proxy_list(proxy_list, filter_by=filter_by)
    
    valid_proxies = []
    for count, proxy in enumerate(proxies, start=1):
        if check_proxy(proxy):
            valid_proxies.append(proxy)
    if not valid_proxies:
        log.warning(f"No valid proxies found - tried {len(proxies)} proxies")
    return [_format_proxy_as_str(proxy) for proxy in valid_proxies]


def get_first_operational_proxy(
                filter_by:dict=None,
                proxy_list:list=None
                ) -> dict:
    """ Returns first valid proxy from the list of passed in proxies (defaults to list from ) """
    if not proxy_list:
        proxy_list = get_proxy_list()
    else:
        log.warning("Using custom proxy list, this is not recommended.")
    
    proxies = _filter_proxy_list(proxy_list, filter_by=filter_by)
    for count, proxy in enumerate(proxies, start=1):
        if check_proxy(proxy):
            log.debug(f"Trying proxy:  ({count} of {len(proxies)})")
            log.info(f"First valid proxy found: {proxy}")
            return _format_proxy_as_str(proxy)
    raise ValueError("No valid proxies found")



from bs4 import BeautifulSoup
import requests
import random

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def proxy_list() -> list:
    """  Returns a dict of proxies scraped from web """
    
    FREE_PROXY_LIST_URL = "https://free-proxy-list.net"
    FREE_PROXY_LIST_URL_UK = "https://free-proxy-list.net/uk-proxy.html"
    
    headers: dict = {
        'Cache-Control': 'no-cache',
        "Pragma": "no-cache"
    }
    r = requests.get(FREE_PROXY_LIST_URL, headers=headers)
    soup = BeautifulSoup(r.content, features="lxml")

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
    return proxy_list


def filtered_proxy_list(filter_by: dict = None)-> list:
    """ 
    Retrieves and filters free proxies (based oon: ip, port, code, country, anonymity, google, https, last_checked)
    Returns:
        -    list of dicts in format: [{'ip': 'port', 'ip': 'port'}, ...]
    """
    filter_func = lambda proxy: [proxy[filter_k] == filter_v for filter_k, filter_v in filter_by.items()]
    return [{proxy['ip']: proxy['port']} for proxy in proxy_list() if all(filter_func(proxy))]


def validate_proxy(proxy: dict) -> bool:
    """ Returns True if proxy is valid, False if not """
    if not proxy:
        log.error("No proxy passed in")
        return
    try:
        proxy = "".join([k+":"+v for k, v in proxy.items()]) # sure there is a better way to do this
        log.debug(f"Validating Proxy: {proxy}")
        response = requests.get("https://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=15)
        log.info(f"Proxy: {proxy} is valid")
        return True
    except Exception as e:
        log.error(f"Proxy: {proxy} is invalid - Exception: {e.__class__.__name__}")
        return False
        

def get_random_proxy(proxies) -> str:
    """ ⛔️ Returns a random proxy from the list of passed in proxies - non validated """
    try:
        return random.choice(proxies)
    except IndexError:
        log.error("No proxies passed in")
        raise


def get_random_valid_proxy(proxies) -> str:
    """ ⛔️ Returns a random valid proxy from the list of passed in proxies - This could be slow because checks all proxies for vaolidaty before selecting one"""
    valid_proxies = []
    for proxy in proxies:
        if validate_proxy(proxy):
            valid_proxies.append(proxy)
    return get_random_proxy(valid_proxies)


def get_first_valid_proxy(proxies) -> str:
    """ ✅  Returns the first valid proxy from the list of passed in proxies """
    if proxies is None:
        log.error("No proxies passed in")
        raise ValueError("No proxies passed in")
    random.shuffle(proxies)
    for proxy in proxies:
        if validate_proxy(proxy):
            return proxy
    log.error("No *valid* proxies found")
    raise

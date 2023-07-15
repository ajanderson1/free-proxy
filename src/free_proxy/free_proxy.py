from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException
import random
import time
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

FREE_PROXY_LIST_URL = "https://free-proxy-list.net"
SPEEDX_PROXY_LIST_URL = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"

PROXY_VALIDATION_URL = "https://www.google.com"
PROXY_VALIDATION_TIMEOUT = 5


def get_first_operational_proxy():
    """ for backwards compatibility """
    log.warning("get_first_operational_proxy() is deprecated, please use ProxyListManager().return_first_operational_proxy() instead")
    return ProxyListManager().return_n_operational_proxies(n=1)[0]


class ProxyDownloader:
    """
    Abstract class for downloading and parsing proxies from a given URL
    """

    def download_and_parse(self, url):
        raise NotImplementedError

    @staticmethod
    def _get_response(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            log.warning(f"Error occurred during download: {e}")
            raise


class SpeedXProxyDownloader(ProxyDownloader):
    def download_and_parse(self, url=SPEEDX_PROXY_LIST_URL):
        response = self._get_response(url)
        if not response:
            return []

        # get the last_modified date from the file header
        last_modified = response.headers.get('Last-Modified')
        if last_modified:
            log.critical(f"Last-Modified: {last_modified}")

        proxy_data = response.text.splitlines()
        proxies = []

        for line in proxy_data:
            ip, port = line.strip().split(":")
            proxy = {'ip': ip, 'port': port}
            proxies.append(proxy)

        return proxies


class FreeProxyListDownloader(ProxyDownloader):
    def download_and_parse(self, url=FREE_PROXY_LIST_URL):
        headers = {
            'Cache-Control': 'no-cache',
            "Pragma": "no-cache"
        }
        response = self._get_response(url)
        if not response:
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find('table', {'class': 'table table-striped table-bordered'})

        #  ensure table is found
        if not table:
            log.warning(f"BS4 failed to find table in response from {url}")
            return []

        proxy_list = []
        for row in table.tbody.findAll('tr'):
            proxy = {
                'ip': row.find_all('td')[0].text,
                'port': row.find_all('td')[1].text,
                'code': row.find_all('td')[2].text,
                'country': row.find_all('td')[3].text,
                'anonymity': row.find_all('td')[4].text,
                'google': row.find_all('td')[5].text,
                'https': row.find_all('td')[6].text,
                'last_checked': row.find_all('td')[7].text
            }
            proxy_list.append(proxy)
        log.debug(f"Retrieved {len(proxy_list)} proxies from web")
        return proxy_list


class ProxyListManager:
    """
    A class for managing a list of proxies from a given source

    Usage:
    To initialise a ProxyListManager with a list of proxies from a given source:
        proxy_list = ProxyListManager(source='TheSpeedX/PROXY-List')  # ...or source='free-proxy-list.net'

    To return the first operational proxy by random from the list:
        proxy_list.get_first_operational_proxy()

    To return the first operational proxy by random from the list that matches a given filter:
        proxy_list.get_first_operational_proxy(filter_by={'country': 'United Kingdom', 'https': 'yes'})

    """

    proxy_downloader = {
        'TheSpeedX/PROXY-List': SpeedXProxyDownloader,
        'free-proxy-list.net': FreeProxyListDownloader
    }

    def __init__(self, source='TheSpeedX/PROXY-List', timeout=5):
        self.source = source
        self.proxies = []
        self.download_proxies()
        self.timeout = timeout

    def download_proxies(self):
        if self.source not in self.proxy_downloader:
            raise ValueError(f"Invalid source: {self.source}. Valid options are: {list(self.proxy_downloader.keys())}")

        downloader = self.proxy_downloader[self.source]()
        self.proxies = downloader.download_and_parse()

    def list_proxies(self):
        return self.proxies

    def list_filterable_keys(self):
        return list(self.proxies[0].keys())

    def filter_proxies(self, filter_by=None):
        if not filter_by:
            log.debug("No `filter_by` argument passed in to _filter_by().")
            return self.proxies

        if not isinstance(filter_by, dict):
            raise TypeError("`filter_by` must be a dict")

        if not all([k in self.proxies[0] for k in filter_by]):
            invalid_keys = [k for k in filter_by if k not in self.proxies[0]]
            raise TypeError(f"`filter_by` contains invalid keys: {invalid_keys}.  All `filter_by` keys must be in the `proxy_list`, valid options are: {list(self.proxies[0].keys())}")


        def filter_func(proxy): return [proxy[filter_k] == filter_v for filter_k, filter_v in filter_by.items()]
        results = [proxy for proxy in self.proxies if all(filter_func(proxy))]

        if not results:
            log.warning(f"Filtering by: {filter_by} returned no results, returning empty list. HINT ...")
            # Assist user with some sample values for each filter_by key they specified.
            sample_size:int  = len(self.proxies) if len(self.proxies) < 3 else 3
            [log.critical(f"Filtering by: '{this_filter_by}' - Sample values: {[proxy[this_filter_by] for proxy in random.sample(self.proxies, sample_size)]}") for this_filter_by in filter_by]

        return results

    def return_n_operational_proxies(self, n=3, filter_by=None, randomise=True):
        if not isinstance(n, int):
            raise TypeError("`n` must be an integer")

        if n < 1:
            raise ValueError("`n` must be greater than 0")

        if len(self.proxies) == 0:
            raise ValueError("No proxies found in list. HINT: Did you forget to call `download_proxies()`?")

        start_time = time.time()
        filtered_proxies = self.proxies

        filtered_proxies = self.filter_proxies(filter_by)

        if randomise:
            random.shuffle(filtered_proxies)

        operational_proxies = []
        for count, proxy in enumerate(filtered_proxies, start=1):
            if ProxyValidator.check_proxy(proxy, timeout=self.timeout or 5):
                operational_proxies.append(ProxyValidator.format_proxy_as_str(proxy))
                if len(operational_proxies) == n:
                    elapsed_time = time.time() - start_time
                    log.info(f"Returning: {operational_proxies}. ({count} of {len(filtered_proxies)}) proxies tried. {elapsed_time:.2f} seconds")
                    return operational_proxies

        raise ValueError(f"Only {len(operational_proxies)} valid proxies found, {n} requested")


class ProxyValidator:
    @staticmethod
    def format_proxy_as_str(proxy):
        if not isinstance(proxy, dict):
            raise TypeError("`proxy` must be a dict")
        return f"{proxy['ip']}:{proxy['port']}"

    @staticmethod
    def format_proxy_as_dict(proxy_str):
        if not isinstance(proxy_str, str):
            raise TypeError("`proxy_str` must be a string")
        ip, port = proxy_str.split(":")
        return {'ip': ip, 'port': port}

    @staticmethod
    def check_proxy(proxy, timeout=5):
        proxy_str = ProxyValidator.format_proxy_as_str(proxy)

        try:
            log.debug(f"Testing proxy: {proxy_str}")
            response = requests.get(PROXY_VALIDATION_URL, proxies={"http": f"http://{proxy_str}", "https": f"http://{proxy_str}"}, timeout=timeout)
            if response.status_code != 200:
                raise RequestException(f"Status Code: {response.status_code}")
            log.debug(f"Proxy: {proxy_str} is valid (status_code: {response.status_code})")
            return True
        except Exception as e:
            log.debug(f"Proxy: {proxy_str} is invalid - Exception: {e.__class__.__name__}")
            return False

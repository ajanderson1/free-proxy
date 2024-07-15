from bs4 import BeautifulSoup
import requests
import random
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, wait

from .config import *

log = logging.getLogger(__name__)


class ProxyDownloader:
    """Abstract base class for downloading and parsing proxies from a given URL."""
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
    """Downloader for proxies from the SpeedX Proxy List."""

    def download_and_parse(self, url=SPEEDX_PROXY_LIST_URL):
        response = self._get_response(url)
        if not response:
            return []

        last_modified = response.headers.get('Last-Modified')
        if last_modified:
            log.info(f"Last-Modified: {last_modified}")

        proxy_data = response.text.splitlines()
        proxies = []

        for line in proxy_data:
            ip, port = line.strip().split(":")
            proxy = {'ip': ip, 'port': port}
            proxies.append(proxy)

        return proxies

class FreeProxyListDownloader(ProxyDownloader):
    """Downloader for proxies from the Free Proxy List."""
    def download_and_parse(self, url=FREE_PROXY_LIST_URL):
        headers = {
            'Cache-Control': 'no-cache',
            "Pragma": "no-cache"
        }
        response = self._get_response(url)
        if not response:
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find(
            'table', {'class': 'table table-striped table-bordered'})

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
    
class ProxyScrapeDownloader(ProxyDownloader):
    """Downloader for proxies from ProxyScrape."""
    def download_and_parse(self, url=PROXY_SCRAPE_URL):
        response = self._get_response(url)
        if not response:
            return []

        proxy_data = response.text.splitlines()
        proxies = []
        log.debug(f"Retrieved {len(proxy_data)} proxies from web")
        log.debug(f"sample proxy: {proxy_data[0]}")

        for line in proxy_data:
            ip, port = line.strip().split(":")
            proxy = {'ip': ip, 'port': port}
            proxies.append(proxy)

        return proxies
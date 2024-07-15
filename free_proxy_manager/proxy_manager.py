import sys
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import threading
import click
import requests

from .proxy_downloader import *
from .proxy_validator import *
from .config import *

proxy_downloaders = {
    'TheSpeedX/PROXY-List': SpeedXProxyDownloader,
    'free-proxy-list.net': FreeProxyListDownloader,
    'proxyscrape.com': ProxyScrapeDownloader,
}

log = logging.getLogger(__name__)


class ProxyManager:
    """
    A class for managing a list of proxies from a given source.

    Usage:
    To initialize a ProxyListManager with a list of proxies from a given source:
        proxy_list_mgr = ProxyListManager(source='TheSpeedX/PROXY-List')  # or source='free-proxy-list.net'

    To return the first operational proxy by random from the list:
        proxy_list_mgr.return_n_operational_proxies(n=1)

    To return the first operational proxy by random from the list that matches a given filter:
        proxy_list_mgr.return_n_operational_proxies(n=1, filter_by={'country': 'US', 'https': 'yes'})
    """

    def __init__(self, source='proxyscrape.com', timeout=5):
        self.source = source
        self.proxies = []
        self.download_proxies()
        self.timeout = timeout
        self.session = requests.Session()

    def download_proxies(self):
        if self.source not in proxy_downloaders:
            raise ValueError(
                f"Invalid source: {self.source}. Valid options are: {list(proxy_downloaders.keys())}")

        downloader = proxy_downloaders[self.source]()
        self.proxies = downloader.download_and_parse()

    def list_proxies(self):
        return self.proxies

    def list_filterable_keys(self):
        return list(self.proxies[0].keys())

    def filter_proxies(self, filter_by=None, surpress_errors=False):
        if not filter_by:
            log.debug("No `filter_by` argument passed in to filter_proxies().")
            return self.proxies

        if not isinstance(filter_by, dict):
            err_msg = f"`filter_by` must be a dict, not a {type(filter_by)}."
            if surpress_errors:
                log.error(err_msg + "  " + "No filter applied.")
                return self.proxies
            else:
                raise TypeError("`filter_by` must be a dict")

        if not all([k in self.proxies[0] for k in filter_by]):
            invalid_keys = [k for k in filter_by if k not in self.proxies[0]]
            err_msg = f"`filter_by` contains invalid keys: {invalid_keys}.  All `filter_by` keys must be in the `proxy_list`, valid options are: {list(self.proxies[0].keys())}.\n - HINT: Some proxy list providers do not provide all fields."
            log.error(err_msg)
            if surpress_errors:
                log.error(err_msg + "  " + "No filter applied.")
                return self.proxies
            else:
                raise TypeError(err_msg)

        def filter_func(proxy): return [
            proxy[filter_k] == filter_v for filter_k, filter_v in filter_by.items()]
        results = [proxy for proxy in self.proxies if all(filter_func(proxy))]

        if not results:
            log.warning(
                f"Filtering by: {filter_by} returned no results, returning empty list.")
            sample_size: int = len(self.proxies) if len(
                self.proxies) < 3 else 3
            [log.warning(f"Filtering by: '{this_filter_by}' - Sample values: {[proxy[this_filter_by] for proxy in random.sample(self.proxies, sample_size)]}")
             for this_filter_by in filter_by]
        log.debug(
            f"Filtering by: {filter_by} returned {len(results)} results.")
        return results

    def return_n_operational_proxies(self, n=1, filter_by=None, max_threads=10, randomise=True):
        if not isinstance(n, int):
            raise TypeError("`n` must be an integer")

        if n < 1:
            raise ValueError("`n` must be greater than 0")

        if len(self.proxies) == 0:
            raise ValueError(
                "No proxies found in list. HINT: Did you forget to call `download_proxies()`?")

        start_time = time.time()  # Record the start time for logging

        # Filter the proxies based on the filter criteria
        filtered_proxies = self.filter_proxies(filter_by)

        # Randomize the order of proxies if specified
        if randomise:
            random.shuffle(filtered_proxies)

        operational_proxies = []  # List to store operational proxies
        stop_event = threading.Event()  # Event to signal when to stop checking proxies
        total_proxies_to_check = len(filtered_proxies)  # Total number of proxies to be checked

        def check_and_append(proxy):
            # If stop_event is set, return None immediately
            if stop_event.is_set():
                return None
            # Check if the proxy is operational
            if ProxyValidator.check_proxy(proxy, self.timeout):
                # Return the formatted proxy string if operational
                return ProxyValidator.format_proxy_as_str(proxy)
            return None

        # Create a ThreadPoolExecutor to check proxies concurrently
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Submit all proxy checks to the executor and store futures in a dictionary
            futures = {executor.submit(check_and_append, proxy): proxy for proxy in filtered_proxies}
            completed_proxies = 0  # Counter for completed operational proxies
            total_proxies_checked = 0  # Counter for total proxies checked

            while completed_proxies < n and futures:
                # Wait for the first future to complete
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                for future in done:
                    result = future.result()  # Get the result of the future
                    total_proxies_checked += 1  # Increment the total proxies checked counter
                    if result:
                        # If the result is an operational proxy, append to the list
                        operational_proxies.append(result)
                        completed_proxies += 1  # Increment the counter
                        if completed_proxies == n:
                            # If the required number of proxies is found, set the stop event
                            stop_event.set()
                            elapsed_time = time.time() - start_time
                            log.info(
                                f"Returning: {operational_proxies}. {total_proxies_checked} of {total_proxies_to_check} proxies tried. {elapsed_time:.2f} seconds")
                            return operational_proxies  # Return the list of operational proxies
                    # Remove the future from the dictionary of futures
                    futures.pop(future)

            elapsed_time = time.time() - start_time
            log.info(f"No more proxies to check. {total_proxies_checked} of {total_proxies_to_check} proxies tried. {elapsed_time:.2f} seconds")

        log.warning(f"{len(operational_proxies)} valid proxies found ({n} requested), returning empty list.")
        return operational_proxies


def get_first_operational_proxy(filter_by=None):
    proxy_list_mgr = ProxyManager()
    log.warning(
        "get_first_operational_proxy() is deprecated, please use ProxyListManager().return_n_operational_proxies() instead")
    return proxy_list_mgr.return_n_operational_proxies(n=1, filter_by=filter_by)[0]


@click.command()
@click.option('--source', default=f'proxyscrape.com', help=f'Source of proxies.  Select from: {list(proxy_downloaders.keys())}')
@click.option('--n', default=1, help='Number of operational proxies to return')
@click.option('--timeout', default=5, help='Timeout for proxy validation')
@click.option('--filter_by', default=None, help='Filter for proxies in the form key:value,key:value')
@click.option('--max_threads', default=10, help='Maximum number of threads for validation')
@click.option('--randomise/--no-randomise', default=True, help='Randomise the order of proxies before validation')
@click.option('--log_level', default='INFO', help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
@click.option('--log_file', default=None, help='Log to a file instead of standard output')
def cli(source, n, timeout, filter_by, max_threads, randomise, log_level, log_file):
    # Configure logging
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(level=log_level, stream=sys.stdout,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    filter_by_dict = None
    if filter_by:
        filter_by_dict = dict(item.split(":") for item in filter_by.split(","))

    proxy_manager = ProxyManager(source=source, timeout=timeout)
    proxies = proxy_manager.return_n_operational_proxies(
        n=n, filter_by=filter_by_dict, max_threads=max_threads, randomise=randomise)

    for proxy in proxies:
        print(proxy)


if __name__ == '__main__':
    cli()

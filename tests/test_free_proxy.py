import pytest

from src.free_proxy.free_proxy import *

import logging
log = logging.getLogger()

def test_proxy_list():
    proxies = proxy_list()
    assert isinstance(proxies, list)
    assert len(proxies) > 0
    assert isinstance(proxies[0], dict)
    assert len(proxies[0]) > 0



def test_filtered_proxy_list():
    proxies = filtered_proxy_list()
    assert isinstance(proxies, list)
    assert len(proxies) > 0
    assert isinstance(proxies[0], dict)
    assert len(proxies[0]) > 0

def test_get_first_valid_proxy():
    proxy = get_first_valid_proxy(filtered_proxy_list())
    assert isinstance(proxy, dict)
    assert len(proxy) > 0

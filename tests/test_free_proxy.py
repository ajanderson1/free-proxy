from free_proxy import get_first_operational_proxy, get_all_operational_proxies, check_proxy
from free_proxy.free_proxy import _format_proxy_as_str, _format_proxy_as_dict

import pytest

import logging
log = logging.getLogger()

# test that _format_proxy_as_str returns a valid proxy_dict and vice versa
@pytest.mark.parametrize("proxy_dict, proxy_str", [
({'ip': '255.255.255.0', 'port': '8080'}, "255.255.255.0:8080"),
])
def test_format_proxy(proxy_dict, proxy_str):
    assert _format_proxy_as_str(proxy_dict) == proxy_str
    assert _format_proxy_as_dict(proxy_str) == proxy_dict

# test that a get_first_operational_proxy returns a valid proxy
def test_get_first_operational_proxy():
    proxy = get_first_operational_proxy()
    log.info(f"First valid proxy found: {proxy}")
    assert check_proxy(proxy)

# test that get_all_operational_proxies returns a list of valid proxies
def test_get_all_operational_proxies():
    proxies = get_all_operational_proxies(filter_by={"country": "United Kingdom", "https": True})
    for proxy in proxies:
        assert check_proxy(proxy)

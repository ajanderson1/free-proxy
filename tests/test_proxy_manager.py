import pytest
import requests
import socket
from click.testing import CliRunner
from free_proxy_manager.proxy_manager import ProxyManager, ProxyValidator, SpeedXProxyDownloader, FreeProxyListDownloader, cli

# Fixtures for proxy managers
@pytest.fixture
def proxy_list_manager_speedx():
    return ProxyManager(source='TheSpeedX/PROXY-List')

@pytest.fixture
def proxy_list_manager_free():
    return ProxyManager(source='free-proxy-list.net')

# Test downloading proxies from different sources
def test_download_proxies_speedx(proxy_list_manager_speedx):
    proxy_list_manager_speedx.download_proxies()
    assert len(proxy_list_manager_speedx.proxies) > 0

def test_download_proxies_free(proxy_list_manager_free):
    proxy_list_manager_free.download_proxies()
    assert len(proxy_list_manager_free.proxies) > 0

# Test filtering proxies by country
def test_filter_proxies_by_country(proxy_list_manager_free):
    proxy_list_manager_free.download_proxies()
    filtered_proxies = proxy_list_manager_free.filter_proxies(filter_by={'country': 'US'})
    assert all(proxy['country'] == 'US' for proxy in filtered_proxies)

# Test filtering proxies by HTTPS support
def test_filter_proxies_by_https(proxy_list_manager_free):
    proxy_list_manager_free.download_proxies()
    filtered_proxies = proxy_list_manager_free.filter_proxies(filter_by={'https': 'yes'})
    assert all(proxy['https'] == 'yes' for proxy in filtered_proxies)

# Test returning n operational proxies with mocking the validator
def test_return_n_operational_proxies(proxy_list_manager_speedx, mocker):
    mocker.patch('free_proxy_manager.proxy_manager.ProxyValidator.check_proxy', return_value=True)
    proxies = proxy_list_manager_speedx.return_n_operational_proxies(n=3)
    assert len(proxies) == 3

# Test the check_proxy function with a valid proxy
def test_check_proxy_valid(mocker):
    proxy = {'ip': '8.8.8.8', 'port': '8080'}
    mock_socket = mocker.Mock()
    mocker.patch('socket.create_connection', return_value=mock_socket)
    mock_socket.recv.return_value = "HTTP/1.1 200 Connection established\r\n\r\n".encode()
    assert ProxyValidator.check_proxy(proxy)

# Test the check_proxy function with an invalid proxy
def test_check_proxy_invalid(mocker):
    proxy = {'ip': '8.8.8.8', 'port': '8080'}
    mocker.patch('socket.create_connection', side_effect=socket.error)
    assert not ProxyValidator.check_proxy(proxy)

# Test initializing ProxyManager with an invalid source
def test_invalid_source():
    with pytest.raises(ValueError):
        ProxyManager(source='invalid-source')

# Test filtering proxies with invalid keys
def test_invalid_filter_keys(proxy_list_manager_free):
    proxy_list_manager_free.download_proxies()
    with pytest.raises(TypeError):
        proxy_list_manager_free.filter_proxies(filter_by={'invalid_key': 'value'})

# Test formatting proxy as string
def test_format_proxy_as_str():
    proxy = {'ip': '8.8.8.8', 'port': '8080'}
    assert ProxyValidator.format_proxy_as_str(proxy) == '8.8.8.8:8080'

# Test formatting proxy as dictionary
def test_format_proxy_as_dict():
    proxy_str = '8.8.8.8:8080'
    assert ProxyValidator.format_proxy_as_dict(proxy_str) == {'ip': '8.8.8.8', 'port': '8080'}

# Test listing proxies
def test_list_proxies(proxy_list_manager_free):
    proxy_list_manager_free.download_proxies()
    proxies = proxy_list_manager_free.list_proxies()
    assert isinstance(proxies, list)
    assert len(proxies) > 0

# Test listing filterable keys
def test_list_filterable_keys(proxy_list_manager_free):
    proxy_list_manager_free.download_proxies()
    keys = proxy_list_manager_free.list_filterable_keys()
    assert isinstance(keys, list)
    assert 'country' in keys
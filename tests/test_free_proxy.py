from free_proxy import *

import pytest
import unittest.mock as mock
from requests.exceptions import RequestException


import logging
log = logging.getLogger()

def test_get_response():
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.raise_for_status.return_value = None  # successful get request
        assert ProxyDownloader()._get_response('https://www.example.com') is not None

        mock_get.return_value.raise_for_status.side_effect = RequestException()  # unsuccessful get request
        with pytest.raises(RequestException):
            ProxyDownloader()._get_response('https://www.example.com')


def test_download_and_parse_speedx():
    with mock.patch.object(SpeedXProxyDownloader, '_get_response', return_value=mock.Mock(text="1.1.1.1:8080\n2.2.2.2:8080")):
        proxies = SpeedXProxyDownloader().download_and_parse()
        assert proxies == [{'ip': '1.1.1.1', 'port': '8080'}, {'ip': '2.2.2.2', 'port': '8080'}]



def test_download_and_parse_free_proxy_list():
    # Create a simple HTML document that mimics the structure of the page at 'https://free-proxy-list.net'
    html_doc = b"""
    <html><body>
    <table class='table table-striped table-bordered'>
    <tbody>
    <tr>
    <td>1.1.1.1</td><td>8080</td><td>US</td><td>United States</td><td>anonymous</td><td>no</td><td>yes</td><td>1 minute ago</td>
    </tr>
    </tbody>
    </table>
    </body></html>
    """
    with mock.patch.object(FreeProxyListDownloader, '_get_response', return_value=mock.Mock(content=html_doc)):
        proxies = FreeProxyListDownloader().download_and_parse()
        assert proxies == [{
            'ip': '1.1.1.1', 
            'port': '8080', 
            'code': 'US', 
            'country': 'United States', 
            'anonymity': 'anonymous', 
            'google': 'no', 
            'https': 'yes', 
            'last_checked': '1 minute ago'
        }]



def test_download_proxies():
    with mock.patch.object(SpeedXProxyDownloader, 'download_and_parse', return_value=[]):
        plm = ProxyListManager(source='TheSpeedX/PROXY-List')
        assert plm.proxies == []

    with mock.patch.object(FreeProxyListDownloader, 'download_and_parse', return_value=[]):
        plm = ProxyListManager(source='free-proxy-list.net')
        assert plm.proxies == []

    with pytest.raises(ValueError):
        ProxyListManager(source='invalid source')


def test_filter_proxies():
    plm = ProxyListManager(source='TheSpeedX/PROXY-List')
    plm.proxies = [{'ip': '1.1.1.1', 'port': '8080'}]

    assert plm.filter_proxies(filter_by={'ip': '1.1.1.1'}) == [{'ip': '1.1.1.1', 'port': '8080'}]
    assert plm.filter_proxies(filter_by={'ip': '2.2.2.2'}) == []
    with pytest.raises(TypeError):
        plm.filter_proxies(filter_by={'invalid_key': 'invalid_value'})
    with pytest.raises(TypeError):
        plm.filter_proxies(filter_by='invalid_filter')


def test_check_proxy():
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200  # valid proxy
        assert ProxyValidator.check_proxy({'ip': '1.1.1.1', 'port': '8080'}) is True

        mock_get.return_value.status_code = 404  # invalid proxy
        assert ProxyValidator.check_proxy({'ip': '1.1.1.1', 'port': '8080'}) is False

        mock_get.side_effect = RequestException()  # request exception
        assert ProxyValidator.check_proxy({'ip': '1.1.1.1', 'port': '8080'}) is False

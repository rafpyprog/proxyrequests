from proxyrequests import *


def test_get_proxies():
    proxies = get_proxies()
    assert isinstance(proxies, list)
    assert proxies != []
    assert all([px['https'] is True for px in proxies])


def test_get_proxies_filter_country():
    country = 'BR'
    proxies = get_proxies(filter_country=country)
    assert proxies != []
    assert all(proxy['country'] == country for proxy in proxies)

    country_list = ('BR', 'JP')
    proxies = get_proxies(filter_country=country_list)
    assert proxies != []
    assert all(proxy['country'] in country_list for proxy in proxies)


def test_ProxyRequests():
    filter_country = ('BR', 'US', 'JP', 'IN')
    prxrequests = ProxyRequests(filter_country=filter_country)
    assert isinstance(prxrequests, ProxyRequests)
    assert len(prxrequests.proxies) <= prxrequests.proxy_servers

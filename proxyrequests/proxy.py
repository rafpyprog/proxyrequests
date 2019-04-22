import random
from subprocess import Popen, PIPE

from bs4 import BeautifulSoup
import dateparser
import requests
from requests.exceptions import ProxyError, SSLError


def get_proxies(https=True, filter_country=None):
    FREE_PROXY_LIST_URL = 'https://free-proxy-list.net/'
    response = requests.get(FREE_PROXY_LIST_URL)
    response.raise_for_status()
    html = BeautifulSoup(response.text, 'lxml')

    table = html.find('table', {'id': 'proxylisttable'}).find_all('tr')
    proxies = []
    keys = ['ip', 'port', 'country', 'country_name', 'anonymity', 'google',
            'https', 'last_checked']
    for linha in table:
        values = [i.text for i in linha.find_all('td')]
        if values:
            proxy = {key: value for key, value in zip(keys, values)}
            proxy['date_checked'] = dateparser.parse(proxy['last_checked'])
            proxy['https'] = True if proxy['https'] == 'yes' else False

            if (https is False) or (https and proxy['https']):
                proxies.append(proxy)

    if filter_country is not None:
        if isinstance(filter_country, str):
            proxies = [i for i in proxies if i['country'] == filter_country]
        if isinstance(filter_country, (list, tuple)):
            proxies = [i for i in proxies if i['country'] in filter_country]

    return proxies



def ping(server, packets=5):
    command = ['ping', '-q', '-c', str(packets), server]
    process = Popen(command, stdout=PIPE, encoding='UTF-8')
    out, err = process.communicate()
    if '100%% packet loss' in out:
        return {'server': server, 'statistics': None}
    ping_statistics = out.splitlines()[-1]
    fields, values = ping_statistics.split('=')
    fields, values = fields[4:-1], values[1:-3]
    statistics = {f: float(v) for f, v in zip(fields.split('/'), values.split('/'))}
    return {'server': server, 'statistics': statistics}



class ProxyRequests():
    def __init__(self, proxy_servers=50, https=True, filter_country=None,
                 max_bad_proxies=10):
        self.https = https
        self.filter_country = filter_country
        self.max_bad_proxies = 10
        self.bad_proxies = 0
        self.proxy_servers = proxy_servers
        self.proxies = self.get_proxies(self.https, self.filter_country)

    def get(self, url, raise_proxy_error=False, **kwargs):
        while True:
            proxy = self.random_proxy
            session = self.set_proxy_session(proxy)
            try:
                r = session.get(url, **kwargs)
            except ProxyError:
                if raise_proxy_error:
                    raise
                print('Cannot connect to {}. Picking new proxy.'.format(proxy['ip']))
                self.remove_bad_proxy(proxy)
            except SSLError:
                if self.https is True:
                    bad_https_msg = 'Cannot connect to {} trought SSL. Picking new proxy.'
                    print(bad_https_msg.format(proxy['ip']))
                    self.remove_bad_proxy(proxy)
                else:
                    raise
            else:
                return r

    @property
    def random_proxy(self):
        proxies_count = len(self.proxies)
        if self.bad_proxies == self.max_bad_proxies:
            print('Too many bad proxies. Renewing server list.')
            self.proxies = self.get_proxies(self.https)
            self.bad_proxies = 0
        return random.choice(self.proxies)

    def get_proxies(self, https, filter_country):
        proxies = get_proxies(https, filter_country)
        proxies = proxies[:self.proxy_servers]
        print('Found {} proxies.'.format(len(proxies)))
        return proxies

    def set_proxy_session(self, proxy):
        session = requests.session()
        proxy = self.random_proxy
        session.proxies = {'http':  '{}:{}'.format(proxy['ip'], proxy['port']),
                           'https': '{}:{}'.format(proxy['ip'], proxy['port'])}
        return session

    def remove_bad_proxy(self, bad_proxy):
        self.proxies = [p for p in self.proxies if p != bad_proxy]
        self.bad_proxies += 1
        print('Removed bad proxy {} from proxies list.'.format(bad_proxy['ip']))
        print('{} proxies remaining / {} bad proxies.'.
              format(len(self.proxies), self.bad_proxies))

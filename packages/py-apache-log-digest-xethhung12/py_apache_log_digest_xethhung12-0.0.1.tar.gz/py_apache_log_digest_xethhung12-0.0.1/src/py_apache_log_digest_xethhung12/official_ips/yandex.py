
import requests
from datetime import datetime
import os
import json
import ipaddress
from py_apache_log_digest_xethhung12.official_ips import common


# url="https://yandex.com/ips"
# rs = requests.get(url, headers={
#     "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0"
# })
# selector = "div.lc-features__description > div > div > p > span"
# print(rs.text)
# soup = BeautifulSoup(rs.text, 'html.parser')
# print(soup.select(selector))
# for ip in [i.text for i in soup.select(selector)]:
#     print(ip)
#     print(ipaddress.ip_network(ip).hosts())
networks = [
    '5.45.192.0/18', '5.255.192.0/18', '37.9.64.0/18', '37.140.128.0/18', '77.88.0.0/18', '84.252.160.0/19', '87.250.224.0/19', '90.156.176.0/20', '92.255.112.0/20', '93.158.128.0/18', '95.108.128.0/17', '141.8.128.0/18', '178.154.128.0/18', '185.32.187.0/24', '213.180.192.0/19'
    #, '2a02:6b8::/29 '
    ]

def get_list_of_yandex_ips(repo: str = "."):
    name="yandex-bot"
    if common.load_ips_json(name, repo) is None:
        ips={}
        for var1 in [name]:
            name=var1
            for network in networks:
                network=network.strip()
                print(network)
                for ip in ipaddress.ip_network(network).hosts():
                    if isinstance(ip, ipaddress.IPv4Address):
                        type_of_ip= "ipv4"
                    elif isinstance(ip, ipaddress.IPv6Address):
                        type_of_ip= "ipv6"
                    ips.update({str(ip): {"ip": str(ip), "ip_type": type_of_ip, "name": name}})
        common.save_ips_json(name, ips, repo)
    return ips

import os
from datetime import datetime
import ipaddress
import requests
import json

def load_time(name: str, repo: str):
    file = f"{name}.last"
    if os.path.exists(file):
        with open(f"{repo}/{name}.last", "r", encoding='utf-8') as f:
            return datetime.strptime(f.read(), "%Y-%m-%d %H:%M:%S")
    else:
        return None

def save_time(name: str, date: datetime, repo: str):
    with open(f"{repo}/{name}.last", "w", encoding='utf-8') as f:
        f.write(datetime.strftime(date, "%Y-%m-%d %H:%M:%S"))

def has_newer(url: str, name: str, repo: str):
    t = load_time(name, repo)
    rs = requests.get(url)
    last_update = datetime.strptime(rs.headers['Last-Modified'], "%a, %d %b %Y %H:%M:%S %Z")

    if t is None:
        return True
    else:
        return last_update > t


def download_standard_ip_list(name: str, url: str, repo: str)->dict:
    dest = {}
    rs = requests.get(url)
    last_update = datetime.strptime(rs.headers['Last-Modified'], "%a, %d %b %Y %H:%M:%S %Z")
    for prefix in rs.json()['prefixes']:
        ip=None
        ip_type=''
        if 'ipv6Prefix' in prefix:
            ip=prefix['ipv6Prefix']
            ip=ipaddress.ip_address(ip[:-3]).exploded
            ip_type='ipv6'            
        if 'ipv4Prefix' in prefix:
            ip=prefix['ipv4Prefix']
            ip=str(ipaddress.ip_address(ip[:-3]))
            ip_type='ipv4'
        if ip is None:
            continue
        
        dest.update({ip: {"ip": ip, "ip_type": ip_type, "name": name}})
    
    # with open(f"{repo}/{name}.data.json", "w", encoding='utf-8') as f:
    #     f.write(json.dumps(dest, indent=2))
    save_ips_json(name, dest, repo)
    save_time(name, last_update, repo)

def save_ips_json(name: str, dest: dict, repo: str):
    with open(f"{repo}/{name}.data.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(dest, indent=2))


def load_ips_json(name: str, repo: str)->dict:
    if not os.path.exists(f"{repo}/{name}.data.json"):
        return None
    with open(f"{repo}/{name}.data.json", "r", encoding='utf-8') as f:
        return json.loads(f.read())
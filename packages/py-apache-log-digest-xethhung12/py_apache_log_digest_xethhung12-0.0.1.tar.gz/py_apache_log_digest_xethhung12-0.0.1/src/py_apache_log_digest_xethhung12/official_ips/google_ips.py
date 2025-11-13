
import requests
from datetime import datetime
import os
import json
import common


bot_list = [
        {"name": "google-bot-common", "url": "https://developers.google.com/static/search/apis/ipranges/googlebot.json"},
        {"name": "google-bot-special", "url": "https://developers.google.com/static/search/apis/ipranges/special-crawlers.json"},
]



def load_google_ips(name: str, repo: str)->dict:
    return common.load_ips_json(name, repo)

def get_list_of_google_ips(repo: str = "."):
    print(f"Repo: {repo}")
    ips={}
    for var1 in bot_list:
        name=var1['name']
        url=var1['url']
        print(f"Processing: {name} - {url}")
        if common.has_newer(url, name, repo):
            print("Updating...")
            common.download_standard_ip_list(name, url, repo)
        loaded = load_google_ips(name, repo)
        if loaded is None:
            raise Exception("Google IPs not exists")
        for ip in loaded:
            ips.update({ip: loaded[ip]})
    return ips

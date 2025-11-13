from py_apache_log_digest_xethhung12.apache.log_processor import decode_access_log, LogModel
from py_apache_log_digest_xethhung12.last_read import LastRead
from py_apache_log_digest_xethhung12.official_ips import yandex
import pandas as pd

def load_access_log(file):
    with open(file, "r", encoding='utf-8') as f:
        log_data = f.read()
        log_data=log_data.split("\n")
        log_data=[decode_access_log(item) for item in log_data if not "" == item.strip()]
        log_data=[var1 for var1 in log_data if var1 is not None]
        # log_data=[unquote(item) for item in log_data ]
    log_data=pd.DataFrame(log_data)
    df = log_data
    return df

def main():
        # print(yandex.get_list_of_yandex_ips())
        last_read = LastRead("/home/xeth/projects/py-apache-digest/access.log", "read.progress")
        list_of_log = list(last_read.read(decode_access_log))
        # print(len(list_of_log))
        import socket

        def get_reverse_name(ip: str):
            return socket.getnameinfo((ip,0),0)[0]
        
        import hashlib
        import json

        def save_map_for_bot(list_of_log):
            with open("map-for-bot.json", "w", encoding='utf-8') as f:
                f.write(json.dumps(map_for_bot, indent=2))
            

        def load_map_for_bot():
            if not os.path.exists("map-for-bot.json"):
                with open("map-for-bot.json", "w", encoding='utf-8') as f:
                    f.write(json.dumps({}, indent=2))
            with open("map-for-bot.json", "r", encoding='utf-8') as f:
                return json.loads(f.read())


        import os
        map_for_bot = load_map_for_bot()

        class X:
            def __init__(self):
                self.index=0
                self.agent_list = {}
            
            def add_agent(self, agent_name: str, agent_value: str):
                self.index+=1
                self.agent_list.update({self.index:{
                    "index": self.index,
                    "name": agent_name,
                    "value": agent_value
                }})
            
            def get_list(self)->str:
                return "\n".join([ f"{self.agent_list[i]['index']} {self.agent_list[i]['name']}" for i in self.agent_list])
            
            def find(self, key: int)->dict:
                if key not in self.agent_list:
                    return None
                else:
                    return self.agent_list[key]


        
        x = X()
        x.add_agent("Google Bot", "google-bot")
        x.add_agent("Apple Bot", "apple-bot")
        x.add_agent("Bing Bot", "bing-bot")
        x.add_agent("MJ12 Bot", "mj12-bot")
        x.add_agent("ChatGPT Bot", "chatgpt-bot")
        x.add_agent("Shap Bot", "shap-bot")
        x.add_agent("Amazon Bot", "amazon-bot")
        x.add_agent("Awario Bot", "awario-bot")
        x.add_agent("Petal Bot", "petal-bot")
        x.add_agent("Semrush Bot", "semrush-bot")
        x.add_agent("X Preview Bot", "x-preview-bot")
        x.add_agent("Perplexity Bot", "perplexity-bot")
        x.add_agent("Yandex Bot", "yandex-bot")

        for i in [i for i in list_of_log if "bot" in i.agent.lower()]:
            agent_hash=hashlib.sha256(i.agent.encode('utf-8')).hexdigest()

            if agent_hash not in map_for_bot:
                type_of_bot =int(input(f"""
Please insert the type of bot
[{i.agent}]

{x.get_list()}
                """))

                print(f"Selected: {type_of_bot}")

                if x.find(type_of_bot) is None:
                    raise Exception("Not found")
                else:
                    v = x.find(type_of_bot)
                    map_for_bot.update({agent_hash: {"type": v["value"], "hash": agent_hash, "agent":i.agent}})
                    save_map_for_bot(map_for_bot)
        
        def is_correct_source(type_of_bot: str, dns_name: str)->bool:
            m = {
                "google-bot": [
                    r"^geo-crawl-\d+-\d+-\d+-\d+\.geo.googlebot\.com$", 
                    r"^crawl-\d+-\d+-\d+-\d+\.googlebot\.com$", 
                    r"^rate-limited-proxy-\d+-\d+-\d+-\d+\.google.com$",
                    r"^\d+_\d+_\d+_\d+\.gae\.googleusercontent.com$",
                    r"^google-proxy-\d+-\d+-\d+-\d+\.google.com$"
                ],
                "amazon-bot": [r"^.*\.amazonbot\.amazon$"],
                "apple-bot": [r"^.*\.applebot\.apple\.com$"],
                "bing-bot": [r".*^.*\.search\.msn\.com$"],
                "awario-bot": [r"^.*\.webmeup\.com$"],
                "mj12-bot": [r"^.*\.mj12bot\.com$"],
                "petal-bot": [r"^.*\.petalsearch\.com$"],
                "yandex-bot": [r"^.*\.yandex\.com$"],
                "semrush-bot": [r"^.*\.semrush\.com$"],
            }

            if type_of_bot not in m:
                return False
            
            import re
            for i in m[type_of_bot]:
                if re.match(i,dns_name):
                    return True
            return False


            

        print("start processing")
        for i in list_of_log:
            if "bot" not in i.agent.lower():
                continue
            agent_hash=hashlib.sha256(i.agent.encode('utf-8')).hexdigest()
            found_name = get_reverse_name(i.ip)
            agent_detail=map_for_bot[agent_hash]
            if is_correct_source(agent_detail['type'], found_name):
                continue
            print(f"Failed {agent_detail['type']}[{i.ip}]: {found_name}")

        

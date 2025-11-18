from py_apache_log_digest_xethhung12.apache.log_processor import decode_access_log, LogModel
from py_apache_log_digest_xethhung12.last_read import LastRead
from py_apache_log_digest_xethhung12.official_ips import yandex
import pandas as pd
import socket
import hashlib
import os
import json

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
    home_dir="/home/xeth/projects/py-apache-digest/logs"
    for f in os.listdir(home_dir):
        # if f in [
        #     "access.log-20251101", "access.log-20250823", "access.log-20250824", "access.log-20250810", 
        #     "access.log-20250822", "access.log-20250915", "access.log-20250901", "access.log-20250904",
        #     "access.log-20251011", "access.log-20250806", "access.log-20250910", "access.log-20250914",
        #     "access.log-20250814", "access.log-20250928", "access.log-20250928", "access.log-20251030",
        #     "access.log-20250820", "access.log-20251020", "access.log-20250830", "access.log-20251107",
        #     "access.log-20250803","access.log-2025082758","access.log-20250827", "access.log-20251015",
        #     "access.log-20251105","access.log-20251017", "access.log-20250917", "access.log-20250812",
        #     "access.log-20251028", "access.log-20251004","access.log-20250801","access.log-20250817",
        #     "access.log-20250907","access.log-20250926","access.log-20250918","access.log-20251112",
        #     "access.log-20251018","access.log-20251027", "access.log-20250913", "access.log-20251019",
        #     "access.log-20250819","access.log-20250903","access.log-20251005","access.log-20250811",
        #     "access.log-20251013","access.log-20250816","access.log-20250807","access.log-20250908",
        #     "access.log-20250908","access.log-20251108","access.log-20251012","access.log-20251025",
        #     "access.log-20250808","access.log-20250924","access.log-20250916","access.log-20251103",
        #     "access.log-20250902","access.log-20250805","access.log-20250909","access.log-20251110",
        #     "access.log-2025101","access.log-20250828","access.log-20251109","access.log-20250815",
        #     "access.log-20250813","access.log-20250906","access.log-20251016","access.log-20250818",
        #     "access.log-20251104","access.log-20250925","access.log-20250911","access.log-20250826",
        #     "access.log-20250921","access.log-20250802","access.log-20250922","access.log-20251102",
        #     "access.log-20251014","access.log-20251022","access.log-20250829","access.log-20250804",
        #     "access.log-20250804","access.log-20250831","access.log-20250809","access.log-20250809",
        #     "access.log-20250920","access.log-20250919","access.log-20251031","access.log-20251106",
        #     "","","","",
        #     "","","","",
        #     "","","","",
        #     "","","","",
        # ]:
        #     continue
        print(f"Processing: {home_dir}/{f}")
        # print(yandex.get_list_of_yandex_ips())
        last_read = LastRead(f, "read.progress")
        list_of_log = list(last_read.read(decode_access_log))
        # print(len(list_of_log))

        def get_reverse_name(ip: str):
            return socket.getnameinfo((ip,0),0)[0]
        

        def save_map_for_bot(list_of_log):
            with open("map-for-bot.json", "w", encoding='utf-8') as f:
                f.write(json.dumps(map_for_bot, indent=2))
            

        def load_map_for_bot():
            if not os.path.exists("map-for-bot.json"):
                with open("map-for-bot.json", "w", encoding='utf-8') as f:
                    f.write(json.dumps({}, indent=2))
            with open("map-for-bot.json", "r", encoding='utf-8') as f:
                return json.loads(f.read())


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
                dd = []
                d=[]
                for index, i in enumerate(self.agent_list):
                    if index != 0 and index % 5 == 0:
                        dd.append(d)
                        d=[]
                    d.append(i)
                if len(d) > 0:
                    dd.append(d)
                
                s=""
                for i in dd:
                    # print(i, self.agent_list)
                    s+="\t".join([f"{self.agent_list[ii]['index']} {self.agent_list[ii]['name']}" for ii in i])
                    s+="\n"
                return s
                    
                # return "\n".join([ f"{self.agent_list[i]['index']} {self.agent_list[i]['name']}" for i in self.agent_list])
            
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
        x.add_agent("ClaudeBot", "claude-bot")
        x.add_agent("AhrefsBot", "ahrefs-bot")
        x.add_agent("SeznamBot", "seznam-bot")
        x.add_agent("DotBot", "dot-bot")
        x.add_agent("SeRankingBot", "se-ranking-bot")
        x.add_agent("QwantBot", "qwant-bot")
        x.add_agent("TwitterBot", "twitter-bot")
        x.add_agent("DuckDuckGoBot", "duck-duck-go-bot")
        x.add_agent("BrightDataBot", "bright-data-bot")
        x.add_agent("YoudaoBot", "youdao-bot")
        x.add_agent("WebSiteInfoNetfoBot", "website-info-net-bot")
        x.add_agent("CoccocBot", "coccoc-bot")
        x.add_agent("HawaiiBot", "hawaii-bot")
        x.add_agent("CommonCrawBot", "commoncrawl-bot")
        x.add_agent("DataForSEOBot", "data-for-seo-bot")
        x.add_agent("DiscordBot", "discord-bot")
        x.add_agent("BitSightBot", "bit-sight-bot")
        x.add_agent("2IPBot", "2ip-bot")
        x.add_agent("ZoomInfoBot", "zoominfo-bot")
        x.add_agent("SlackBot", "slack-bot")
        x.add_agent("YakBot", "yak-bot")
        x.add_agent("ArchiveOrgBot", "archive-org-bot")
        x.add_agent("HaloBot", "halo-bot")
        x.add_agent("BacklinksExtendedBot", "backlings-extended-bot")
        x.add_agent("PinterestBot", "pinterest-bot")
        x.add_agent("MixrankBot", "mixrand-bot")
        x.add_agent("ABEvalBot", "abeval-bot")
        x.add_agent("NanaleiBot", "hanalei-bot")
        x.add_agent("SeekportBot", "seekport-bot")
        x.add_agent("IBouBot", "ibou-bot")
        x.add_agent("TelegramBot", "telegram-bot")
        x.add_agent("PandaSecurityBot", "panda-security-bot")
        x.add_agent("AliBot", "ali-bot")
        x.add_agent("GoParserBot", "go-parser-bot")
        x.add_agent("OrbBot", "orb-bot")
        x.add_agent("WpBot", "wp-bot")
        x.add_agent("GoRedirectCheckerBot", "go-redirect-checker-bot")
        x.add_agent("SEOZoomBot", "seo-zoom-bot")
        x.add_agent("RobotsHarvesterBot", "robot-harvester-bot")
        x.add_agent("SpeedyIndexBot", "speedy-index-bot")
        x.add_agent("AcademicBot", "academic-bot")
        x.add_agent("AASABot", "aasa-bot")
        x.add_agent("RobotsSitemapsFetcherBot", "robot-site-map-fetcher-bot")
        x.add_agent("SerpstatBot", "serpstat-bot")
        x.add_agent("WanScannerBot", "wan-scanner-bot")
        x.add_agent("WordPressBot", "wordpress-bot")
        x.add_agent("WRTNBot", "wrtn-bot")
        x.add_agent("AIHitBot", "aihit-bot")
        x.add_agent("SuperBot", "super-bot")
        x.add_agent("RSSFeedIndexBot", "rss-feed-index-bot")
        x.add_agent("WellKnownBot", "well-known-bot")
        x.add_agent("RobotsFetcherBot", "robot-fetcher-bot")
        x.add_agent("MakeMerryBot", "make-merry-bot")
        x.add_agent("T3VersionBot", "t3-version-bot")
        x.add_agent("QuoraBot", "quora-bot")
        x.add_agent("ThinkBot", "think-bot")
        x.add_agent("TimpiBot", "timpi-bot")
        x.add_agent("LMArenaUnfurlBot", "lm-arena-unfurl-bot")
        x.add_agent("KeysSoBot", "keys-so-bot")
        x.add_agent("YaDirectFetcherBot", "ya-direct-fetcher-bot")
        x.add_agent("KapigoBot", "kapigo-bot")
        x.add_agent("FaceBot", "face-bot")
        x.add_agent("ZaldamoSearchBot", "zaldamo-search-bot")
        x.add_agent("SiteCheckerBot", "site-checker-bot")
        x.add_agent("SEOBilityBot", "seo-bility-bot")
        x.add_agent("WebzioBot", "webzio-bot")
        x.add_agent("TrenditionBot", "trendition-bot")
        x.add_agent("SiteOverPagesBot", "site-over-pages-bot")
        x.add_agent("IAskBot", "i-ask-bot")
        x.add_agent("IntelXIOBot", "intel-x-io-bot")
        x.add_agent("StripeBot", "stripe-bot")
        x.add_agent("ScannerBot", "scanner-bot")
        x.add_agent("SiderBot", "sider-bot")
        x.add_agent("BlexBot", "blex-bot")
        x.add_agent("JoomlaCheckBot", "joomla-check-bot")

        for i in [i for i in list_of_log if i is not None and i.agent is not None and "bot" in i.agent.lower()]:
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
                    print(f"Selected: {v['name']}")
        
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
                "se-ranking-bot": [r"^.*\.sr-srv\.net$"],
                "qwant-bot": [r"^.*\.qwant\.com$"],
                "commoncrawl-bot": [r"^.*\.crawl\.commoncrawl\.org$"],
            }

            if type_of_bot not in m:
                return False
            
            import re
            for i in m[type_of_bot]:
                if re.match(i,dns_name):
                    return True
            return False


            

        continue
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

        

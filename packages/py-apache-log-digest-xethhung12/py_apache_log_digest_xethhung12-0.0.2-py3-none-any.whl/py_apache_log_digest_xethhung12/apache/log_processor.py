from urllib.parse import unquote
import re
from dataclasses import dataclass
import pandas as pd
from datetime import datetime
import json
import requests

@dataclass
class LogModel:
    ip: str
    identd: str
    user: str
    date: datetime
    method: str
    url: str
    httpVersion: str
    httpResponse: str
    size: str
    referer: str
    agent: str

    @staticmethod
    def from_tuple(t):
        try:
            ip, identd, user, date, method, url, httpVersion, httpResponse, size, referer, agent = t
            url = unquote(url)
            return LogModel(ip,identd,user,date,method, url, httpVersion,httpResponse, size, referer, agent)
        except Exception as ex:
            print(f"Fail to process: {t}")
            raise ex
            
    def as_dict(self):
        from dataclasses import asdict
        return asdict(self)
        
def decode_access_log(input: str):
    reg_pattern = "^(?P<ip>\\S*) ([-]) ([-]) \\[(?P<date>.*)\\]\\s\"(?P<httpMethod>\\S*)\\s(?P<url>\\S*)\\s(?P<httpVersion>[^\"]*)\"\\s(?P<responseCode>\\S*)\\s(?P<size>\\S*)\\s\"(?P<referer>[^\"]*)\"\\s\"(?P<agent>.*)\"$"
    result1 = re.match(reg_pattern, input)
    if result1 is None:
        reg_pattern2 = "^(?P<ip>\\S*) ([-]) ([-]) \\[(?P<date>.*)\\]\\s\"-\"\\s(?P<responseCode>\\S*)\\s(?P<size>\\S*)\\s\"(?P<referer>[^\"]*)\"\\s\"(?P<agent>.*)\"$"
        result2 = re.match(reg_pattern2, input)
        if result2 is not None:
            ip, identd, user, date, httpResponse, size, referer, agent = result2.groups()
            return LogModel.from_tuple((ip, identd, user, date,"","","", httpResponse, size, referer, agent))    
        else:
            return None
            # raise Exception(f"unexpect log format: `{input}`")
    else:
        return LogModel.from_tuple(result1.groups())

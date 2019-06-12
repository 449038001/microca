# encoding=utf-8
import json
import datetime
from utils.config import *
import base64
import requests


def send_to_dingding(message, user_mobile, ignoreUrl, successUrl):
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Basic ' + base64.b64encode(dingding_basic),
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    data = {
        "msgtype": "action_card",
        "msgcontent": {
            "title": "淘宝开放平台 session(Access Token)到期提醒",
            "markdown": message,
            "btn_orientation": "1",
            "btn_json_list": [
                {
                    "title": "不再提醒",
                    "action_url": ignoreUrl
                },
                {
                    "title": "完成续期",
                    "action_url": successUrl
                }
            ]
        },
        "mobile_list": user_mobile
    }
    try:
        print requests.post(dingding_url, headers=headers, data=json.dumps(data)).text
    except:
        pass


# 检查是否过期，如果过期返回True,未过期为false
def check_valid(end_time, delta):
    return end_time - datetime.timedelta(days=delta) < datetime.datetime.now() < end_time

# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 3:38 PM
# @Author  : Ma1tobiose
# @File    : runReminders.py
# @Software: PyCharm
import json
import os
from utils.check_update import *
from reminder import Mongo

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def remind(end_time, valid_delta, message, force_delta, data, ignore_url, update_url):
    not_ignore_tel = [i for i in data['tel'] if data['tel'][i] == 0]
    valid = check_valid(end_time, valid_delta)
    # 还有10天过期，且没有点击忽略提醒，每天提示
    if valid and data['ignore'] is 0 and data['updated'] is 0 and len(not_ignore_tel)>0:
        send_to_dingding(message, not_ignore_tel, ignore_url, update_url)
    # 差2天还没有确认的，无视忽略提醒强制提醒
    if check_valid(end_time, force_delta) and data['updated'] is 0:
        send_to_dingding(message, data['tel'].keys(), ignore_url, update_url)


if __name__ == '__main__':
    sessions = Mongo.coll['session'].find()
    for index, session in enumerate(sessions):
        end_time = datetime.datetime.strptime(session['end_time'], "%Y-%m-%d")
        force_delta = 2
        message = u"[Test]您的开放平台 session **" + session["appKey"] + u" " + session["nick"] + u"** 即将过期，过期日期为：**" + session[
            'end_time'] + u"**"
        update_url = "https://xx.com/session/update/" + str(session['_id'])
        ignore_url = "https://xx.com/session/ignore/" + str(session['_id'])
        remind(end_time, 10, message, force_delta, session, ignore_url, update_url)

    certs_offline = Mongo.coll['certs_offline'].find()
    for index, cert in enumerate(certs_offline):
        force_delta = 7
        end_time = datetime.datetime.strptime(cert['end_time'].encode('utf-8'), "%Y-%m-%d")
        message = u"您的证书 **" + cert['id'] + u"** 即将过期，过期日期为：**" + cert['end_time'] + u"**"
        update_url = "https://xx.com/certOff/update/" + str(cert['_id'])
        ignore_url = "https://xx.com/certOff/ignore/" + str(cert['_id'])
        remind(end_time, 30, message, force_delta, cert, ignore_url, update_url)


# -*- coding: utf-8 -*-
# @Time    : 2019/3/25 5:05 PM
# @Author  : Ma1tobiose
# @File    : importFromFile.py
# @Software: PyCharm
import json
import os
from utils import cert_utils, check_update
from utils.conn import MongoDB


Mongo = MongoDB()

if __name__ == '__main__':
    pfx_pass = json.load(open(os.path.join('../certs/pass.json')))
    sessions = json.load(open(os.path.join('../certs/sessions.json')))
    for index, session in enumerate(sessions):
        session_detail = {
            'id': index,
            'account': session[0],
            'app': session[1],
            'appKey': session[2],
            'nick': session[3],
            'end_time': session[4],
            'period': session[5],
            'owner': session[6],
            'tel': {i: 0 for i in session[7]},
            'ignore': 0,
            'updated': 0
        }
        Mongo.coll['session'].update({"id": index}, {"$set": session_detail}, upsert=True)

    certs_details = {}
    path = '../certs'
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename == "pass.json" or filename == '.DS_Store' or filename == 'sessions.json':
                continue
            issued_to, issued_by, start_time, end_time = cert_utils.get_cert_details(dirpath, filename, pfx_pass)
            valid = check_update.check_valid(end_time, 30)
            start_time = start_time.strftime('%Y-%m-%d')
            end_time = end_time.strftime('%Y-%m-%d')
            cert_detail = {'id': filename, 'issued_to': issued_to, 'issued_by': issued_by,
                           'start_time': start_time, 'ignore': 0,
                           'end_time': end_time,
                           'valid': '已过期' if valid else '未过期',
                           'owner': pfx_pass[filename][1],
                           'update_date': pfx_pass[filename][3],
                           'from_cert': pfx_pass[filename][4],
                           'tel': {i: 0 for i in pfx_pass[filename][2]},
                           'updated': 0
                           }
            Mongo.coll['certs_offline'].update({"id": filename}, {"$set": cert_detail}, upsert=True)
            certs_details[filename] = cert_detail

# encoding=utf-8
from flask import *
from utils import cert_utils
from utils.config import *
from hashlib import md5
import re
import requests
import base64
import random
import string
from utils.conn import MongoDB
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)
Mongo = MongoDB()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/gen')
def gen_p12():
    username, phone = get_email_by_token()
    try:
        user_p12 = gen_user_p12(username, phone)
        response = make_response(user_p12)
        response.headers["Content-type"] = "application/octet-stream"
        response.headers["Content-Disposition"] = "attachment; filename=" + md5(username).hexdigest() + ".p12"
        return response
    except:
        return index()


def get_email_by_token():
    _security_token_inc = request.cookies.get('_security_token_inc')
    headers = {
        'cookie': '_security_token_inc=' + _security_token_inc
    }
    try:
        data = json.loads(requests.get(
            'sso',
            headers=headers).text[41:-2])['data']
        return data['email'], data['userPhone']
    except:
        print('error when check email')
        return None


def check_username(username):
    email = get_email_by_token()
    if len(re.findall('\w+?@xx\.com', username)) > 0 and email == username:
        return True
    else:
        return False


def send_password_to_dingding(password, user_mobile):
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Basic ' + base64.b64encode(dingding_basic),
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    data = {
        "msgtype": "text",
        "msgcontent": {
            "content": u"您的证书密码是" + password
        },
        "mobile_list": [
            user_mobile
        ]
    }
    try:
        requests.post(dingding_url, headers=headers, data=json.dumps(data)).text
    except:
        pass


def gen_user_p12(username, phone):
    subj = "".join(["cn=" + username + ",st=Zhejiang,L=Hangzhou,C=CN,",
                    "O=Ma1tobiose, OU=test"])
    user_key = cert_utils.genkey(2048)
    user_csr = cert_utils.gencsr(subj, user_key)
    user_crt = cert_utils.sign_csr(user_csr, root_key, root_crt, ca=False)
    password = gen_password()
    send_password_to_dingding(password, phone)
    p12 = cert_utils.p12(user_crt, user_key, username, password)

    return p12


def gen_password(slen=8):
    return ''.join(random.sample(string.ascii_letters + string.digits, slen))


@app.route('/certList')
def list():
    certs_detail = Mongo.coll['certs_offline'].find()
    return render_template('cert_list.html', cert_detail=certs_detail)


@app.route('/sessionList')
def sessionList():
    sessions_detail = Mongo.coll['session'].find()
    return render_template('session_list.html', sessions_detail=sessions_detail)


@app.route('/certOff/ignore/<id>')
def ignoreCertOff(id):
    try:
        email, phone = get_email_by_token()
        cert = Mongo.coll['certs_offline'].find_one({"_id": ObjectId(id)})
        tel = cert['tel']
        tel[phone] = 1
        if phone not in cert['tel'].keys():
            return "您没有权限"

        Mongo.coll['certs_offline'].update({"_id": ObjectId(id)}, {"$set": {'tel': tel}})
        return "已不再提醒"
    except:
        return "error"


@app.route('/certOff/update/<id>')
def updateCertOff(id):
    try:
        # check session
        email, phone = get_email_by_token()
        cert = Mongo.coll['certs_offline'].find_one({"_id": ObjectId(id)})
        if phone not in cert['tel'].keys():
            return "您没有权限"
        end_time = datetime.datetime.strptime(cert['end_time'], "%Y-%m-%d")
        new_end_time = datetime.datetime.now() + datetime.timedelta(days=int(cert['period']))
        if abs(end_time - datetime.datetime.now()) > datetime.timedelta(days=int(cert['period']) * 1.5):
            return "更新日期与当前日期差距过大"
        Mongo.coll['certs_offline'].update({"_id": ObjectId(id)},
                                           {"$set": {"updated": 1, "end_time": new_end_time.strftime("%Y-%m-%d")}})
        return "更新成功"
    except:
        return "更新错误"


@app.route('/session/update/<id>')
def updateSession(id):
    try:
        email, phone = get_email_by_token()
        session = Mongo.coll['session'].find_one({"_id": ObjectId(id)})
        if phone not in session['tel'].keys():
            return "您没有权限"
        end_time = datetime.datetime.strptime(session['end_time'], "%Y-%m-%d")
        new_end_time = datetime.datetime.now() + datetime.timedelta(days=int(session['period']))
        if abs(end_time - datetime.datetime.now()) > datetime.timedelta(days=int(session['period']) * 1.5):
            return "更新日期与当前日期差距过大"
        Mongo.coll['session'].update({"_id": ObjectId(id)},
                                     {"$set": {"updated": 1, "end_time": new_end_time.strftime("%Y-%m-%d")}})
        return "更新成功"
    except:
        return "更新错误"


@app.route('/session/ignore/<id>')
def ignoreSession(id):
    try:
        email, phone = get_email_by_token()
        session = Mongo.coll['session'].find_one({"_id": ObjectId(id)})
        tel = session['tel']
        tel[phone] = 1
        if phone not in session['tel'].keys():
            return "您没有权限"
        Mongo.coll['session'].update({"_id": ObjectId(id)}, {"$set": {'tel': tel}})
        return "已不再提醒"
    except:
        return "error"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8898)


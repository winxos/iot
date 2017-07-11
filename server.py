# -*- coding: utf-8 -*-
# iot demo
# winxos , AISTLAB,2017-06-24
from flask import Flask, request, make_response, send_file, render_template
import json
from datetime import datetime
import uuid
import base64
from flask_login import LoginManager
from flask_qrcode import QRcode

app = Flask(__name__)
lm = LoginManager()
lm.init_app(app)
qrcode = QRcode(app)


# @lm.user_loader()
# def load_user(id):
#     return User.get(id)


def reg_uuid(s):
    uid = uuid.uuid3(uuid.NAMESPACE_DNS, s)
    suid = base64.b64encode(uid.bytes)[:-2]
    return str(suid, encoding="utf8")


@app.route('/')
def hello_world():
    return 'Hello IOT, AISTLab!'


DEVICES = {}


@app.route('/create', methods=['GET'])
def create():
    if request.method == 'GET':
        token = request.args.get("token")
        suid = reg_uuid(str(datetime.now()))
        if suid not in DEVICES:
            DEVICES[suid] = []
        print(DEVICES)
        return make_response(suid)
    make_response("ok")


@app.route('/query', methods=['GET'])
def query():
    if request.method == 'GET':
        id = request.args.get("id")
        print(DEVICES)
        if id not in DEVICES:
            s = "ERROR,DEVICE NOT EXIST."
        else:
            s = DEVICES[id]
            count = request.args.get("count")
            if count:
                return make_response(" ".join(s[-int(count):]))
            else:
                return make_response(" ".join(s))
    return make_response("ok")


@app.route('/update', methods=['GET'])
def update():
    if request.method == 'GET':
        id = request.args.get("id")
        if id in DEVICES:
            value = request.args.get("value")
            if value:
                DEVICES[id].append(value)
                return make_response("Y")
        return make_response("N")
    return make_response("ok")


@app.route('/remove', methods=['GET'])
def remove():
    if request.method == 'GET':
        id = request.args.get("id")
        if id in DEVICES:
            del DEVICES[id]
            return make_response("Y")
        else:
            return make_response("N")
    return make_response("ok")


@app.route('/list', methods=['GET'])
def list():
    if request.method == 'GET':
        # return send_file(
        #     qrcode("hello iot", mode='raw'),
        #     mimetype='image/png',
        #     cache_timeout=0)
        list = []
        for n in DEVICES:
            list.append((n, n))
        return render_template('list.html', list=list)
    return make_response("ok")


@app.route('/qr')
def qr():
    if request.method == 'GET':
        id = request.args.get("id")
        return send_file(
            qrcode(id, mode='raw', error_correction="H", box_size=3),
            mimetype='image/png',
            cache_timeout=0)


if __name__ == '__main__':
    app.run(debug=True, port=999)

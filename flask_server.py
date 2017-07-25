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
from flask_socketio import SocketIO
import socket

UDP_SERVER_IP, UDP_SERVER_PORT = "192.168.8.128", 9999
HTTP_SERVER_IP, HTTP_SERVER_PORT = "192.168.8.128", 999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'passed'

lm = LoginManager()
lm.init_app(app)
qrcode = QRcode(app)
socketio = SocketIO(app)


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
        suid = reg_uuid(str(datetime.now()))
        if suid not in DEVICES:
            DEVICES[suid] = {"num": len(DEVICES), "state": "ready"}
        return make_response(suid)
    make_response("ok")


@app.route('/query', methods=['GET'])
def query():
    if request.method == 'GET':
        id = request.args.get("id")
        if id not in DEVICES:
            s = "ERROR,DEVICE NOT EXIST."
        else:
            s = DEVICES[id]
            return make_response(str(s))
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
            list.append((n, DEVICES[n]))
        return render_template('list.html', list=list, cache_timeout=0)
    return make_response("ok")


@app.route('/unlock', methods=['GET'])
def unlock():
    if request.method == 'GET':
        id = request.args.get("id")
        sock.sendto(("id=%s;cmd=unlock" % id).encode("utf8"), (UDP_SERVER_IP, UDP_SERVER_PORT))
        # if id in DEVICES:
        #     DEVICES[id]["state"] = "using"
        #     return render_template("using.html", l=id)
        # else:
        #     return make_response("ERROR")
    return make_response("ok")


@app.route('/lock', methods=['GET'])
def lock():
    if request.method == 'GET':
        id = request.args.get("id")
        if id in DEVICES:
            DEVICES[id]["state"] = "ready"
            return make_response("SUCCESS")
        else:
            return make_response("ERROR")
    return make_response("ok")


@app.route('/qr')
def qr():
    if request.method == 'GET':
        id = request.args.get("id")
        return send_file(
            qrcode("http://%s:%d/unlock?id=" % (HTTP_SERVER_IP, HTTP_SERVER_PORT) + id, mode='raw',
                   error_correction="H",
                   box_size=3),
            mimetype='image/png',
            cache_timeout=0)


@app.route('/item')
def item():
    if request.method == 'GET':
        id = request.args.get("id")
        if id in DEVICES:
            return render_template("item.html", l=(id, DEVICES[id]))
        else:
            print(id)
            return make_response("ERROR")
    return make_response("ok")


@app.route('/init')
def init():
    if request.method == 'GET':
        while len(DEVICES) < 1000:
            create()
        return "finished"


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=HTTP_SERVER_PORT)

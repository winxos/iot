# -*- coding: utf-8 -*-
# iot demo
# winxos , AISTLAB,2017-06-24
from flask import Flask, request, make_response
import json
from datetime import datetime
import uuid
import base64

app = Flask(__name__)


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
            DEVICES[suid] = "0"
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
        return make_response(s)
    return make_response("ok")


@app.route('/update', methods=['GET'])
def update():
    if request.method == 'GET':
        id = request.args.get("id")
        if id in DEVICES:
            value = request.args.get("value")
            if value:
                DEVICES[id] = value
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


if __name__ == '__main__':
    app.run(debug=True, port=999)

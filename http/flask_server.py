# -*- coding: utf-8 -*-
# iot demo
# winxos , AISTLAB,2017-06-24
from flask import Flask, request, make_response, send_file, render_template, Response, session
from datetime import datetime
import uuid
import base64
from flask_login import LoginManager
from flask_qrcode import QRcode
import redis
import time
from flask_socketio import SocketIO, send, emit

pool = redis.ConnectionPool(host='localhost', port=6379, db=1)
r = redis.StrictRedis(connection_pool=pool)

HTTP_SERVER_IP, HTTP_SERVER_PORT = "iot.aistl.com", 999

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


def hash_message(d_s):
    ds = d_s.split(';')  # format a=a1;b=b1;c=c1
    cs = {}
    for d in ds:  # get args
        ds = d.split('=')
        if len(ds) > 1:  # has = symbol
            cs[ds[0]] = ds[1]
    return cs


@socketio.on('my event')
def handle_my_custom_event(json):
    emit('my response', json, namespace='/chat')


@app.route('/pubsub')
def pubsub():
    print("pubsub in.")
    p = r.pubsub()
    p.subscribe(['device'])
    cache = {}
    print("first cache:%s" % cache)

    def get_data(s, cache):
        print("get_data in.")
        for item in p.listen():
            print(item)
            if item['type'] == 'message':
                data = item['data']
                ds = hash_message(data.decode('utf8'))
                if 'ret' in ds:
                    if ds['ret'] == 'error':
                        if ds['state'] == 'using' and ds['user'] == s['id']:
                            print('user:    %s' % ds['user'])
                            break
                cache['ret'] = 'success'
                yield 'data:%s\n\n' % data
        cache['ret'] = "error"
        cache['msg'] = "using"
        print("get_data out.")
        yield 'data:%s\n\n' % "the device is using."

    tmp = session.copy()
    resp = get_data(tmp, cache)
    next(resp)
    print(cache)
    if 'ret' in cache:
        print(cache['ret'])
        if cache['ret'] == 'error':
            print('ret:%s' % cache['ret'])
            p.unsubscribe('device')
            return make_response("%s" % cache['ret'])
    print("pubsub out.")
    return Response(resp, mimetype="text/event-stream")


@app.route('/unlock', methods=['GET'])
def unlock():
    if request.method == 'GET':
        print("sub")
        if "id" in session:
            print("%s already" % session["id"])
        else:  # first
            session["id"] = reg_uuid(str(time.time()))
            print("%s first login" % session["id"])
        id = request.args.get("sid")
        r.publish('user', 'sid=%s;user=%s;cmd=unlock' % (id, session["id"]))
        return render_template("index.html")
    return make_response("ok")


@app.route('/qr')
def qr():
    if request.method == 'GET':
        id = request.args.get("id")
        return send_file(
            qrcode("http://%s:%d/unlock?sid=" % (HTTP_SERVER_IP, HTTP_SERVER_PORT) + id, mode='raw',
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
    app.run(host="0.0.0.0", debug=False, port=HTTP_SERVER_PORT, threaded=True)

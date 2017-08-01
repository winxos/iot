# -*- coding: utf-8 -*-
# iot udp server demo
# winxos , AISTLAB,2017-07-24
import socketserver
import socket
from datetime import datetime
import logging
import os
import redis
import threading

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # DGRAM -> UDP

logging.basicConfig(filename=os.path.join(os.getcwd(), 'log.txt'), filemode='w', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')
DEVICES = {}
pool = redis.ConnectionPool(host='localhost', port=6379, db=1)
r = redis.StrictRedis(connection_pool=pool)
p = r.pubsub()
p.subscribe(['user'])


def hash_message(d_s):
    ds = d_s.split(';')  # format a=a1;b=b1;c=c1
    cs = {}
    for d in ds:  # get args
        ds = d.split('=')
        if len(ds) > 1:  # has = symbol
            cs[ds[0]] = ds[1]
    return cs


class RedisListener(threading.Thread):
    '''
    Redis pubsub
    http server <->Redis<-> udp server
    and pass message through
    '''

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            for item in p.listen():
                logging.debug(item)
                if item['type'] == 'message':
                    data = item['data']
                    d_s = data.decode('utf8')
                    logging.debug("[sub received]%s[end]" % d_s)
                    cs = hash_message(d_s)
                    if 'sid' in cs:  # from http server
                        if cs['sid'] in DEVICES:
                            if 'cmd' in cs:
                                if cs['cmd'] == 'unlock':
                                    if DEVICES[cs['sid']]["state"] == "idle":
                                        socket.sendto("\x00\x00\x02\x00".encode("utf8"), DEVICES[cs['sid']]["address"])
                                        logging.info("unlocking %s" % cs['sid'])
                                    else:
                                        r.publish('device', 'id=%s;ret=error;state=using' % cs['sid'])
                                        logging.info("The device %s is using. " % cs['sid'])
                        else:
                            r.publish('device', 'id=%s;ret=error;state=offline' % cs['sid'])
                            logging.debug("The device %s is offline. " % cs['sid'])
                    else:
                        logging.debug("[pubsub]wrong format.")


class MyUDPHandler(socketserver.BaseRequestHandler):
    '''
    udp server <-> devices
    '''

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        d_s = data.decode('utf8')
        logging.debug("[udp received]%s[end]from:%s" % (self.client_address[0], d_s))
        cs = hash_message(d_s)
        if 'id' in cs:
            if cs['id'] not in DEVICES:  # first login
                DEVICES[cs['id']] = {"state": "idle", "address": self.client_address}
                logging.debug("DEVICE %s added in." % cs['id'])
            else:  # already online
                if 'data' in cs:  # have data, pass to web server
                    ds = cs['data'].split(' ')
                    logging.info('[data]%s[end]' % ' '.join(ds))
                    r.publish("device", 'id=%s;data=%s' % (cs['id'], ' '.join(ds)))
                if 'state' in cs:
                    if cs['state'] == "locked":
                        DEVICES[cs['id']]["state"] = 'idle'
                        r.publish("device", 'id=%s;state=locked' % cs['id'])
                    elif cs['state'] == "unlocked":
                        DEVICES[cs['id']]["state"] = 'using'
                        r.publish("device", 'id=%s;state=unlocked' % cs['id'])
            DEVICES[cs['id']]["last_alive"] = int(datetime.now().timestamp())
        else:
            logging.debug("[udp]wrong format.")
        logging.debug(DEVICES)


if __name__ == "__main__":
    rl = RedisListener()
    rl.setDaemon(True)
    rl.start()
    HOST, PORT = "0.0.0.0", 9999
    sever = socketserver.ThreadingUDPServer((HOST, PORT), MyUDPHandler)
    sever.serve_forever()  # 通过调用对象的serve_forever()方法来激活服务端

# -*- coding: utf-8 -*-
# iot udp server demo
# winxos , AISTLAB,2017-07-24
import socketserver
from datetime import datetime
import logging
import os

logging.basicConfig(filename=os.path.join(os.getcwd(), 'log.txt'), filemode='w', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')
DEVICES = {}


class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        d_s = data.decode('utf8')
        logging.debug("[udp received]%s[end]from:%s" % (self.client_address[0], d_s))
        ds = d_s.split(';')  # format a=a1;b=b1;c=c1
        cs = {}
        for d in ds:  # get args
            ds = d.split('=')
            if len(ds) > 1:  # has = symbol
                cs[ds[0]] = ds[1]
        if 'sid' in cs:  # from http server
            if cs['sid'] in DEVICES:
                if 'cmd' in cs:
                    if cs['cmd'] == 'unlock':
                        if DEVICES[cs['sid']]["state"] == "idle":
                            socket.sendto("\x00\x00\x02\x00".encode("utf8"), DEVICES[cs['sid']]["address"])
                            logging.info("unlocking %s" % cs['sid'])
                            DEVICES[cs['sid']]["notify"] = {"user": "", "address": self.client_address}
                        else:
                            socket.sendto("The device is using.".encode("utf8"), self.client_address)
                            logging.info("The device %s is using. " % cs['sid'])
            else:
                socket.sendto("The device lose connection.".encode("utf8"), self.client_address)
                logging.debug("The device %s not found." % cs['sid'])
        elif 'id' in cs:
            if cs['id'] not in DEVICES:  # first login
                DEVICES[cs['id']] = {"state": "idle", "address": self.client_address}
                logging.debug("DEVICE %s added in." % cs['id'])
            else:  # already online
                if 'data' in cs:  # have data, pass to web server
                    ds = cs['data'].split(' ')
                    logging.info('[data] %s' % ' '.join(ds))
                    if "notify" in DEVICES[cs['id']]:
                        socket.sendto(("data=%s" % ' '.join(ds)).encode("utf8"), DEVICES[cs['id']]["notify"]["address"])
                if 'state' in cs:
                    if cs['state'] == "locked":
                        DEVICES[cs['id']]["state"] = 'idle'
                        socket.sendto(("state=locked").encode("utf8"), DEVICES[cs['id']]["notify"]["address"])
                    elif cs['state'] == "unlocked":
                        DEVICES[cs['id']]["state"] = 'using'
                        socket.sendto(("state=unlocked").encode("utf8"), DEVICES[cs['id']]["notify"]["address"])
            DEVICES[cs['id']]["last_alive"] = int(datetime.now().timestamp())
        else:
            socket.sendto(data.upper(), self.client_address)
        logging.debug(DEVICES)


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    sever = socketserver.ThreadingUDPServer((HOST, PORT), MyUDPHandler)
    sever.serve_forever()  # 通过调用对象的serve_forever()方法来激活服务端

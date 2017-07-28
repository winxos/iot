# -*- coding: utf-8 -*-
# iot udp server demo
# winxos , AISTLAB,2017-07-24
import socketserver
from datetime import datetime
import logging
import os

logging.basicConfig(filename=os.path.join(os.getcwd(), 'log.txt'), filemode='w', level=logging.DEBUG)
DEVICES = {}


class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        d_s = data.decode('utf8')
        logging.debug("[%s] %s" % (self.client_address[0], d_s))
        ds = d_s.split(';')  # format a=a1;b=b1;c=c1
        cs = {}
        for d in ds:  # get args
            ds = d.split('=')
            if len(ds) > 1:  # has = symbol
                cs[ds[0]] = ds[1]
        if 'id' in cs:
            if cs['id'] not in DEVICES:  # first login
                DEVICES[cs['id']] = {"state": "idle", "address": self.client_address}
                # DEVICES[cs['id']]["socket"].sendto("first time".encode("utf8"), self.client_address)
            else:
                # DEVICES[cs['id']]["socket"].sendto("already".encode("utf8"), self.client_address)
                pass
            DEVICES[cs['id']]["last_alive"] = int(datetime.now().timestamp())
            if 'cmd' in cs:
                if cs['cmd'] == 'unlock':
                    socket.sendto("\x00\x00\x02\x00".encode("utf8"), DEVICES[cs['id']]["address"])
                    logging.debug("unlocking %s" % cs['id'])
        logging.debug(DEVICES)
        socket.sendto(data.upper(), self.client_address)


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    sever = socketserver.ThreadingUDPServer((HOST, PORT), MyUDPHandler)
    sever.serve_forever()  # 通过调用对象的serve_forever()方法来激活服务端

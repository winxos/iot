import socket
import threading
import time

server_host, server_port = "localhost", 9999
id = "123456"
data = "id=%s;cmd=login" % id

is_exit = False

state = "idle"
event = None


class getcmd(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        global event
        while not is_exit:
            try:
                cmd = input('input:')
                if cmd == "lock":
                    event = "locking"
                else:
                    self.sock.sendto(bytes(cmd, 'utf8'), (server_host, server_port))
            except Exception as e:
                print("[error] %s" % e)


class listener(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        global event
        while not is_exit:
            try:
                data, addr = self.sock.recvfrom(1024)
                print("[debug] %s:%s" % (addr, data))
                if data[3] == 0:
                    print('unlocked')
                    event = "unlocking"
            except Exception as e:
                print("[listen err] %s" % e)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 10001))
    sock.sendto(bytes(data, 'utf8'), (server_host, server_port))

    l = listener(sock)
    l.setDaemon(True)
    l.start()
    print("listening...")
    t = getcmd(sock)
    t.setDaemon(True)  # important
    t.start()
    try:
        while t.isAlive() and l.isAlive():
            if state == 'idle':
                if event == "unlocking":
                    sock.sendto(("id=%s;state=unlocked" % id).encode("utf8"), (server_host, server_port))
                    event = None
                    state = "using"
            elif state == 'using':
                if event == "locking":
                    sock.sendto(("id=%s;state=locked" % id).encode("utf8"), (server_host, server_port))
                    state = 'idle'
                    event = None
    except KeyboardInterrupt:
        print("[sys err] user stop.")
    is_exit = True
    print("server exit.")
    t.join()
    l.join()

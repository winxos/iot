import socket
import threading
import time

server_host, server_port = "localhost", 9999
data = "id=1233456;cmd=login"

is_exit = False


class getcmd(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        while not is_exit:
            try:
                cmd = input()
                self.sock.sendto(bytes(cmd, 'utf8'), (server_host, server_port))
            except Exception as e:
                print("[shell err] %s" % e)


class listener(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        while not is_exit:
            try:
                data, addr = self.sock.recvfrom(1024)
                print("[debug] %s:%s" % (addr, data))
            except Exception as e:
                print("[listen err] %s" % e)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 10001))
    sock.sendto(bytes(data, 'utf8'), (server_host, server_port))
    t = getcmd(sock)
    t.setDaemon(True)  # important
    t.start()
    l = listener(sock)
    l.setDaemon(True)
    l.start()
    print("listening...")
    try:
        while t.isAlive() and l.isAlive():
            pass
    except KeyboardInterrupt:
        print("[sys err] user stop.")
    is_exit = True
    print("server exit.")
    t.join()
    l.join()

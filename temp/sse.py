from flask import Flask, render_template, Response, request, make_response
import time
import socket
import redis

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # DGRAM -> UDP

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"

pool = redis.ConnectionPool(host='localhost', port=6379, db=1)
r = redis.StrictRedis(connection_pool=pool)
p = r.pubsub()
p.subscribe(['device'])


@app.route('/stream')
def stream():
    def event_stream():
        while True:
            time.sleep(1)
            yield 'data:%s\n\n' % time.asctime(time.localtime(time.time()))

    return Response(event_stream(), mimetype="text/event-stream")


@app.route('/message')
def message():
    def udp_listener():
        i = 0
        while True:
            try:
                s.sendto(("%d" % i).encode('utf8'), ("localhost", 9999))
                i = i + 1
                data, addr = s.recvfrom(1024)
                # print("%s:%s" % (addr, data))
                yield 'data:%s\n\n' % data
            except Exception as e:
                print("[listen err] %s" % e)

    return Response(udp_listener(), mimetype="text/event-stream")


@app.route('/pubsub')
def pubsub():
    def get_data():
        for item in p.listen():
            print(item)
            if item['type'] == 'message':
                data = item['data']
                yield 'data:%s\n\n' % data
                if item['data'] == 'over':
                    break;
        p.unsubscribe('iot')

    return Response(get_data(), mimetype="text/event-stream")


@app.route('/unlock')
def unlock():
    if request.method == 'GET':
        id = request.args.get("id")
        r.publish('user', 'id=%s;cmd=unlock' % id)
    return make_response("ok")


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=999, threaded=True)

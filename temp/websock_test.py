import os
from flask import Flask, render_template, session, request, make_response
from flask_socketio import SocketIO, send, emit
import redis
import threading

app = Flask(__name__)
app.secret_key = "guess_the_number"  # for demo purpose only. This should really be kept secret to ensure sensitive data is kept secure!
socketio = SocketIO(app)

pool = redis.ConnectionPool(host='localhost', port=6379, db=1)
r = redis.StrictRedis(connection_pool=pool)


class Listener(threading.Thread):
    def __init__(self, r, channels):
        threading.Thread.__init__(self)
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)

    def subscribe(self, s):
        self.pubsub.subscribe(s)

    def run(self):
        for item in self.pubsub.listen():
            print(item)
            if item['type'] == 'message':
                socketio.send(item['data'].decode('utf8'))


l = Listener(r, "user")
l.start()


@app.route('/')
def root():
    return render_template("ws.html")


@socketio.on("connect")
def on_connect():
    print("Client connected!")


@socketio.on("disconnect")
def on_disconnect():
    print("Client disconnected!")
    session.clear()


@socketio.on("message")
def on_message(msg):
    print(msg)
    send(msg.upper())


@app.route('/unlock', methods=['GET'])
def unlock():
    if request.method == 'GET':
        print("sub")
        if "id" in session:
            print("%s already" % session["id"])
        else:  # first
            session["id"] = "www"
        id = request.args.get("sid")
        l.subscribe("u%s" % id)
        r.publish('device', 'sid=%s;user=%s;cmd=unlock' % (id, session["id"]))
        return render_template("ws.html")
    return make_response("ok")


if __name__ == '__main__':
    if 'PORT' in os.environ:  # running on Heroku
        socketio.run(app, host="0.0.0.0", port=int(os.environ['PORT']))
    else:  # running locally
        socketio.run(app, debug=True)

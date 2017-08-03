import os
from flask import Flask, render_template, session
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.secret_key = "guess_the_number"  # for demo purpose only. This should really be kept secret to ensure sensitive data is kept secure!
socketio = SocketIO(app)


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


if __name__ == '__main__':
    if 'PORT' in os.environ:  # running on Heroku
        socketio.run(app, host="0.0.0.0", port=int(os.environ['PORT']))
    else:  # running locally
        socketio.run(app, debug=True)

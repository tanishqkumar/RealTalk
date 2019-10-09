import os
from flask import Flask, session, redirect, render_template, request, jsonify, url_for
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from flask_session import Session
from functools import wraps
from datetime import datetime
import simplejson as json
from collections import deque

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# initialising the login required functionality
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/register")
        return f(*args, **kwargs)
    return decorated_function

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

namesTaken = []
channels = []
channelsMessages = dict()

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html", channels=channels)
    if request.method == "POST":
        channelName = request.form.get("channelName")
        if channelName in channels:
            return render_template("error.html", error = "Sorry, channel already exists. Try another name or join this channel from the drop-down menu.")
        else:
            channels.append(channelName)
            channelsMessages[channelName] = deque()
            session['currentChannel'] = channelName
            return redirect(("/channel/%s" %(channelName)))

@app.route("/channel/<channelName>", methods=["GET", "POST"])
@login_required
def channel(channelName):
     if request.method == "GET":
         session['currentChannel'] = channelName
         currentChannel = session.get('currentChannel')
         return render_template("channeltemplate.html", channels = channels, channelName = channelName, messages = channelsMessages[currentChannel])
     if request.method == "POST":
         return False

# need to implement send message functionality for chat room here
@socketio.on('submit message')
def someEvent(data):
    author = session.get("user_id")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # anytime a message is passed into the back-end, we need to create a new entry in channelsMessages
    currentChannel = session.get('currentChannel')
    if len(channelsMessages[currentChannel]) > 100:
        channelsMessages[currentChannel].popleft()
        channelsMessages[currentChannel].append({'message': data['message'], 'author': author, 'timestamp': timestamp})
    else:
        channelsMessages[currentChannel].append({'message': data['message'], 'author': author, 'timestamp': timestamp})
    emit('broadcast message', {'message': data['message'], 'author': author, 'timestamp': timestamp}, broadcast=True, room=currentChannel)

# need to implement join functionality for chat room here
@socketio.on('joined')
def on_join():
    room = session.get('currentChannel')
    join_room(room)
    author = session.get("user_id")
    emit('joined', {'author': author}, room=room)

# need to implement leave functionality for chat room here
@socketio.on('left')
def on_leave():
    room = session.get('currentChannel')
    author = session.get("user_id")
    leave_room(room)
    emit('left', {'author': author}, room=room)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", channels=channels)
    else:
        username = request.form.get("username")
        if username in namesTaken:
            return render_template("error.html", error = "Name currently exists, try another one.")
        else:
            session["user_id"] = username
            namesTaken.append(username)
            return redirect("/")

@app.route("/logout")
@login_required
def logout():
    namesTaken.remove(session.get("user_id"))
    session.clear()
    return redirect("/register")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session

# application opject with flask constructor
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'    # Use the filesystem to store session data

# Initialize flask session with the app
Session(app)

# Create a SocketIO instance, passing the Flask app and managing session explicitly
socketio = SocketIO(app, manage_session=False)

# Define a route for the root URL ('/') using both GET and POST methods
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')    # Render the 'index.html' template when accessing the root URL

# Define a route for the '/chat' URL using both GET and POST methods
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        username = request.form['username']
        room = request.form['room']
        # Store data in session
        session['username'] = username
        session['room'] = room
        return render_template('chat.html', session = session)
    else:
        if session.get('username') is not None:
            return render_template('chat.html', session = session)
        else:
            return redirect(url_for('index'))

# SocketIO event: 'join' - triggered when a user joins a chat room
@socketio.on('join', namespace = '/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('username') + ' has entered the room.'}, room = room)

# SocketIO event: 'text' - triggered when a user sends a message
@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    emit('message', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)

# SocketIO event: 'left' - triggered when a user leaves the chat room
@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)

# Run the Flask application with SocketIO support
if __name__ == '__main__':
    socketio.run(app)
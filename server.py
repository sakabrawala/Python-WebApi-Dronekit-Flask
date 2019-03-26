from flask import Flask, render_template
from flask_socketio import SocketIO
import dronekit
import sys
import socket
import threading
import time
import signal


socket.socket._bind = socket.socket.bind
def my_socket_bind(self, *args, **kwargs):
    self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return socket.socket._bind(self, *args, **kwargs)
socket.socket.bind = my_socket_bind
# okay, now that that's done...

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def pyr(vehicle):
    while True:
        time.sleep(.5)
        atti = vehicle.attitude
        if atti:
            socketio.emit('pyr_status', {
                "Pitch": atti.pitch,
                "Yaw": atti.yaw,
                "Roll": atti.roll,
                })
        else:
            socket.emit('pyr_status', None)

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) >= 2 else '/dev/ttyACM0'
    print 'Connecting to ' + target + '...'
    vehicle = dronekit.connect(target)
    vehiclethread2 = threading.Thread(target=pyr, args=(vehicle,))
    vehiclethread2.start()
    socketio.run(app, host="0.0.0.0", port=8080)



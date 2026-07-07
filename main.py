import os
from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
# CORS ayarları sayesinde GitHub Pages'tan gelen isteklere izin veriyoruz
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('message')
def handle_message(data):
    # Gelen mesajı, bağlı olan diğer herkese aynen fırlatıyoruz
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)

import eventlet
import socketio
import json
import os

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

# Mesajları kaydetmek için dosya ismi
DB_FILE = 'mesajlar.json'

# Eğer dosya yoksa boş bir liste oluştur
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        json.dump([], f)

def load_messages():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_message(data):
    messages = load_messages()
    messages.append(data)
    # Sadece son 50 mesajı tutalım ki dosya şişmesin
    if len(messages) > 50:
        messages = messages[-50:]
    with open(DB_FILE, 'w') as f:
        json.dump(messages, f)

active_users = []

@sio.event
def connect(sid, environ):
    print("Yeni bağlantı: ", sid)

@sio.event
def join(sid, data):
    user = data['user']
    active_users.append({'sid': sid, 'user': user})
    
    # Yeni gelene geçmiş mesajları gönder
    sio.emit('history', load_messages(), to=sid)
    # Güncel kullanıcı listesini yayınla
    sio.emit('user_list', [u['user'] for u in active_users])

@sio.on('message')
def handle_message(sid, data):
    save_message(data)
    sio.emit('message', data)

@sio.event
def disconnect(sid):
    global active_users
    active_users = [u for u in active_users if u['sid'] != sid]
    sio.emit('user_list', [u['user'] for u in active_users])

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

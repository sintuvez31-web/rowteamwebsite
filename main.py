import socketio
import eventlet
from pymongo import MongoClient

# MongoDB Bağlantısı
client = MongoClient("mongodb+srv://sintuvez31_db_user:W6jvjQPbm2GUU3b6@cluster0.m2fb3ty.mongodb.net/?appName=Cluster0")
db = client['rowteam_db']
collection = db['messages']

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

active_users = []

@sio.event
def connect(sid, environ):
    print("Yeni bağlantı: ", sid)

@sio.event
def join(sid, data):
    user = data['user']
    active_users.append({'sid': sid, 'user': user})
    
    # MongoDB'den son 50 mesajı çek ve gönder
    history = list(collection.find().sort("_id", -1).limit(50))
    for msg in history:
        msg.pop('_id', None)
    
    sio.emit('history', history[::-1], to=sid)
    sio.emit('user_list', [u['user'] for u in active_users])

@sio.on('message')
def handle_message(sid, data):
    # MongoDB'ye kaydet
    collection.insert_one(data)
    sio.emit('message', data)

@sio.event
def disconnect(sid):
    global active_users
    active_users = [u for u in active_users if u['sid'] != sid]
    sio.emit('user_list', [u['user'] for u in active_users])

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

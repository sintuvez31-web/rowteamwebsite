import os
from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
# CORS ayarlarıyla frontend bağlantılarına izin veriyoruz
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Sunucu açık olduğu sürece mesajları ve aktif kullanıcıları bellekte tutuyoruz
messages_history = []
active_users = {}  # {sid: username} şeklinde tutulacak

@socketio.on('connect')
def handle_connect():
    print("Bir kullanıcı bağlandı.")

@socketio.on('join')
def handle_join(data):
    username = data.get('user', '@anonim')
    # Kullanıcının socket ID'sini isme eşliyoruz
    active_users[request.sid] = username
    
    # 1. Yeni giriş yapan kullanıcıya eski mesaj geçmişini gönder
    emit('history', messages_history)
    
    # 2. Herkese güncel aktif kullanıcı listesini yayınla
    emit('user_list', list(set(active_users.values())), broadcast=True)

@socketio.on('message')
def handle_message(data):
    # Gelen mesajı geçmiş listesine ekle
    messages_history.append(data)
    # Eğer geçmiş çok şişmesin istersen son 50 mesajı tutabilirsin:
    if len(messages_history) > 50:
        messages_history.pop(0)
        
    # Mesajı gönderen dahil herkese dağıt (broadcast=True)
    emit('message', data, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    # Kullanıcı sayfayı kapattığında veya F5 attığında listeden sil
    if request.sid in active_users:
        disconnected_user = active_users[request.sid]
        del active_users[request.sid]
        # Kalan aktif kullanıcı listesini herkese yeniden gönder
        emit('user_list', list(set(active_users.values())), broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)

import socket
import threading
import json
from datetime import datetime

class ChatServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}
        self.rooms = {'general': []}
        self.running = True
        
    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            print("=" * 50)
            print("✅ СЕРВЕР ЗАПУЩЕН")
            print(f"📍 Адрес: {self.host}:{self.port}")
            print("📡 Ожидание подключений...")
            print("=" * 50)
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"🔌 Подключен клиент: {address}")
                    
                    thread = threading.Thread(target=self.handle_client, 
                                            args=(client_socket, address),
                                            daemon=True)
                    thread.start()
                    
                except Exception as e:
                    if self.running:
                        print(f"❌ Ошибка: {e}")
                    
        except Exception as e:
            print(f"❌ Ошибка запуска сервера: {e}")
    
    def handle_client(self, client_socket, address):
        client_name = None
        current_room = 'general'
        
        try:
            while True:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                message = json.loads(data)
                
                if message['type'] == 'login':
                    client_name = message['name']
                    self.clients[client_socket] = {
                        'name': client_name,
                        'room': current_room
                    }
                    
                    # Отправляем приветствие
                    welcome = {
                        'type': 'system',
                        'text': f'Добро пожаловать, {client_name}!'
                    }
                    client_socket.send(json.dumps(welcome).encode('utf-8'))
                    
                    # Отправляем список комнат
                    rooms_response = {
                        'type': 'rooms',
                        'rooms': list(self.rooms.keys())
                    }
                    client_socket.send(json.dumps(rooms_response).encode('utf-8'))
                    
                    # Уведомляем других
                    self.broadcast({
                        'type': 'system',
                        'text': f'✨ {client_name} присоединился к чату!'
                    }, 'general', exclude=client_socket)
                    
                    # Отправляем список пользователей
                    self.send_user_list(client_socket)
                    
                    print(f"👤 {client_name} вошел в чат")
                    
                elif message['type'] == 'message':
                    if client_name:
                        msg = {
                            'type': 'message',
                            'name': client_name,
                            'text': message['text'],
                            'timestamp': datetime.now().strftime("%H:%M")
                        }
                        self.broadcast(msg, current_room)
                        print(f"💬 {client_name}: {message['text']}")
                
                elif message['type'] == 'join_room':
                    new_room = message['room']
                    if new_room in self.rooms and new_room != current_room:
                        self.broadcast({
                            'type': 'system',
                            'text': f'👋 {client_name} покинул комнату'
                        }, current_room)
                        
                        current_room = new_room
                        self.clients[client_socket]['room'] = current_room
                        
                        self.broadcast({
                            'type': 'system',
                            'text': f'🎉 {client_name} присоединился к комнате!'
                        }, current_room)
                        
                        self.send_user_list(client_socket)
                        print(f"🔄 {client_name} перешел в комнату {new_room}")
                
                elif message['type'] == 'create_room':
                    new_room = message['room'].strip()
                    if new_room and new_room not in self.rooms:
                        self.rooms[new_room] = []
                        rooms_response = {
                            'type': 'rooms',
                            'rooms': list(self.rooms.keys())
                        }
                        self.broadcast_to_all(rooms_response)
                        print(f"📁 Создана новая комната: {new_room}")
                
                elif message['type'] == 'get_rooms':
                    response = {
                        'type': 'rooms',
                        'rooms': list(self.rooms.keys())
                    }
                    client_socket.send(json.dumps(response).encode('utf-8'))
                
                elif message['type'] == 'get_users':
                    self.send_user_list(client_socket)
                        
        except Exception as e:
            print(f"❌ Ошибка с клиентом {address}: {e}")
        finally:
            if client_name:
                print(f"👋 {client_name} покинул чат")
                if client_socket in self.clients:
                    del self.clients[client_socket]
                
                self.broadcast({
                    'type': 'system',
                    'text': f'🚪 {client_name} покинул чат'
                }, current_room)
            
            try:
                client_socket.close()
            except:
                pass
    
    def broadcast(self, message, room, exclude=None):
        """Отправить сообщение всем в комнате"""
        for client_socket, info in self.clients.items():
            if info['room'] == room and client_socket != exclude:
                try:
                    client_socket.send(json.dumps(message).encode('utf-8'))
                except:
                    pass
    
    def broadcast_to_all(self, message):
        """Отправить сообщение всем клиентам"""
        message_json = json.dumps(message)
        for client_socket in list(self.clients.keys()):
            try:
                client_socket.send(message_json.encode('utf-8'))
            except:
                pass
    
    def send_user_list(self, client_socket):
        """Отправить список пользователей"""
        if client_socket in self.clients:
            current_room = self.clients[client_socket]['room']
            users = [
                self.clients[c]['name']
                for c in self.clients
                if self.clients[c]['room'] == current_room
            ]
            response = {
                'type': 'users',
                'users': users
            }
            try:
                client_socket.send(json.dumps(response).encode('utf-8'))
            except:
                pass
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()

if __name__ == "__main__":
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
        server.stop()
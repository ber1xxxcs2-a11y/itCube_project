import socket
import threading
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox, font
from datetime import datetime

class ModernChatClient:
    def __init__(self):
        self.client_socket = None
        self.name = None
        self.current_room = 'general'
        self.running = True
        
        # Цветовая схема
        self.colors = {
            'bg': '#1a1a1a',
            'sidebar': '#2d2d2d',
            'header': '#242424',
            'input': '#3a3a3a',
            'accent': '#2b9c5c',
            'accent_hover': '#237d4a',
            'text': '#e0e0e0',
            'text_secondary': '#888888',
            'my_message': '#2b9c5c',
            'other_message': '#3a3a3a',
            'system': '#ffa500'
        }
        
        # Создаем главное окно
        self.window = tk.Tk()
        self.window.title("Modern Messenger")
        self.window.geometry("1100x700")
        self.window.configure(bg=self.colors['bg'])
        self.window.minsize(800, 500)
        
        # Создаем интерфейс входа
        self.create_login_ui()
        
    def create_login_ui(self):
        """Создание интерфейса входа"""
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Основной контейнер
        container = tk.Frame(self.window, bg=self.colors['bg'])
        container.pack(expand=True)
        
        # Логотип
        logo_label = tk.Label(container, text="💬", font=("Segoe UI", 80), 
                             bg=self.colors['bg'], fg=self.colors['accent'])
        logo_label.pack(pady=(0, 10))
        
        title = tk.Label(container, text="Modern Messenger", 
                        font=("Segoe UI", 28, "bold"),
                        bg=self.colors['bg'], fg=self.colors['text'])
        title.pack(pady=(0, 30))
        
        # Поле ввода имени
        name_frame = tk.Frame(container, bg=self.colors['bg'])
        name_frame.pack(pady=10)
        
        name_label = tk.Label(name_frame, text="Ваше имя", font=("Segoe UI", 11),
                              bg=self.colors['bg'], fg=self.colors['text_secondary'])
        name_label.pack(anchor='w')
        
        self.name_entry = tk.Entry(name_frame, font=("Segoe UI", 12), width=30,
                                   bg=self.colors['input'], fg=self.colors['text'],
                                   insertbackground=self.colors['accent'],
                                   relief='flat', bd=2)
        self.name_entry.pack(pady=(5, 0), ipady=8)
        
        # Поле сервера
        server_frame = tk.Frame(container, bg=self.colors['bg'])
        server_frame.pack(pady=10)
        
        server_label = tk.Label(server_frame, text="Адрес сервера", font=("Segoe UI", 11),
                                bg=self.colors['bg'], fg=self.colors['text_secondary'])
        server_label.pack(anchor='w')
        
        self.server_entry = tk.Entry(server_frame, font=("Segoe UI", 12), width=30,
                                     bg=self.colors['input'], fg=self.colors['text'],
                                     insertbackground=self.colors['accent'],
                                     relief='flat', bd=2)
        self.server_entry.insert(0, 'localhost')
        self.server_entry.pack(pady=(5, 0), ipady=8)
        
        # Поле порта
        port_frame = tk.Frame(container, bg=self.colors['bg'])
        port_frame.pack(pady=10)
        
        port_label = tk.Label(port_frame, text="Порт", font=("Segoe UI", 11),
                              bg=self.colors['bg'], fg=self.colors['text_secondary'])
        port_label.pack(anchor='w')
        
        self.port_entry = tk.Entry(port_frame, font=("Segoe UI", 12), width=30,
                                   bg=self.colors['input'], fg=self.colors['text'],
                                   insertbackground=self.colors['accent'],
                                   relief='flat', bd=2)
        self.port_entry.insert(0, '5555')
        self.port_entry.pack(pady=(5, 0), ipady=8)
        
        # Кнопка подключения
        self.connect_btn = tk.Button(container, text="Подключиться", 
                                     command=self.connect_to_server,
                                     font=("Segoe UI", 12, "bold"),
                                     bg=self.colors['accent'], fg='white',
                                     activebackground=self.colors['accent_hover'],
                                     activeforeground='white',
                                     relief='flat', bd=0, cursor='hand2',
                                     width=25, pady=10)
        self.connect_btn.pack(pady=30)
        
        # Статус
        self.status_label = tk.Label(container, text="", font=("Segoe UI", 10),
                                     bg=self.colors['bg'], fg=self.colors['accent'])
        self.status_label.pack(pady=10)
    
    def connect_to_server(self):
        """Подключение к серверу"""
        self.name = self.name_entry.get().strip()
        server = self.server_entry.get().strip()
        port_str = self.port_entry.get().strip()
        
        if not self.name:
            self.status_label.config(text="❌ Введите ваше имя!", fg='#ff4444')
            return
        
        try:
            port = int(port_str)
        except ValueError:
            self.status_label.config(text="❌ Неверный порт!", fg='#ff4444')
            return
        
        self.connect_btn.config(text="Подключение...", state='disabled')
        self.status_label.config(text=f"🔄 Подключение к {server}:{port}...", fg=self.colors['accent'])
        self.window.update()
        
        def connect_thread():
            try:
                # Создаем сокет
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((server, port))
                sock.settimeout(None)
                
                # Сохраняем сокет
                self.client_socket = sock
                
                # Отправляем логин
                login_data = json.dumps({'type': 'login', 'name': self.name})
                self.client_socket.send(login_data.encode('utf-8'))
                
                # Запускаем прием сообщений
                receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
                receive_thread.start()
                
                # Переключаемся на интерфейс чата
                self.window.after(0, self.create_chat_ui)
                
            except socket.timeout:
                self.window.after(0, lambda: self.status_label.config(
                    text="❌ Таймаут подключения!", fg='#ff4444'))
                self.window.after(0, lambda: self.connect_btn.config(
                    text="Подключиться", state='normal'))
                messagebox.showerror("Ошибка", "Таймаут подключения!\nУбедитесь, что сервер запущен.")
            except ConnectionRefusedError:
                self.window.after(0, lambda: self.status_label.config(
                    text="❌ Сервер не отвечает!", fg='#ff4444'))
                self.window.after(0, lambda: self.connect_btn.config(
                    text="Подключиться", state='normal'))
                messagebox.showerror("Ошибка", f"Сервер {server}:{port} не отвечает!\n\nЗапустите server.py")
            except Exception as e:
                self.window.after(0, lambda: self.status_label.config(
                    text=f"❌ Ошибка: {str(e)[:30]}", fg='#ff4444'))
                self.window.after(0, lambda: self.connect_btn.config(
                    text="Подключиться", state='normal'))
                messagebox.showerror("Ошибка", f"Ошибка подключения:\n{str(e)}")
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def create_chat_ui(self):
        """Создание интерфейса чата"""
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Основной контейнер
        main_container = tk.Frame(self.window, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель
        left_panel = tk.Frame(main_container, width=260, bg=self.colors['sidebar'])
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)
        
        # Заголовок левой панели
        header_left = tk.Frame(left_panel, bg=self.colors['header'], height=60)
        header_left.pack(fill=tk.X)
        header_left.pack_propagate(False)
        
        tk.Label(header_left, text="📁 КОМНАТЫ", font=("Segoe UI", 12, "bold"),
                bg=self.colors['header'], fg=self.colors['text']).pack(pady=15)
        
        # Список комнат
        rooms_frame = tk.Frame(left_panel, bg=self.colors['sidebar'])
        rooms_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        rooms_scroll = tk.Scrollbar(rooms_frame, bg=self.colors['sidebar'])
        rooms_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.rooms_listbox = tk.Listbox(rooms_frame, bg=self.colors['sidebar'],
                                        fg=self.colors['text'], font=("Segoe UI", 10),
                                        selectbackground=self.colors['accent'],
                                        selectforeground='white',
                                        relief='flat', bd=0,
                                        yscrollcommand=rooms_scroll.set)
        self.rooms_listbox.pack(fill=tk.BOTH, expand=True)
        rooms_scroll.config(command=self.rooms_listbox.yview)
        self.rooms_listbox.bind('<Double-Button-1>', self.join_room)
        
        # Создание комнаты
        create_frame = tk.Frame(left_panel, bg=self.colors['sidebar'])
        create_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.new_room_entry = tk.Entry(create_frame, font=("Segoe UI", 10),
                                       bg=self.colors['input'], fg=self.colors['text'],
                                       relief='flat')
        self.new_room_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        create_btn = tk.Button(create_frame, text="+", command=self.create_room,
                              bg=self.colors['accent'], fg='white',
                              font=("Segoe UI", 14, "bold"), width=3,
                              relief='flat', cursor='hand2')
        create_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Центральная панель
        center_panel = tk.Frame(main_container, bg=self.colors['bg'])
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Верхняя панель
        chat_header = tk.Frame(center_panel, bg=self.colors['header'], height=60)
        chat_header.pack(fill=tk.X)
        chat_header.pack_propagate(False)
        
        self.room_label = tk.Label(chat_header, text="Общий чат", 
                                   font=("Segoe UI", 14, "bold"),
                                   bg=self.colors['header'], fg=self.colors['text'])
        self.room_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Статус
        self.online_status = tk.Label(chat_header, text="● В сети", 
                                      font=("Segoe UI", 9),
                                      bg=self.colors['header'], fg=self.colors['accent'])
        self.online_status.pack(side=tk.RIGHT, padx=20)
        
        # Область сообщений
        self.chat_area = scrolledtext.ScrolledText(center_panel, wrap=tk.WORD,
                                                   bg=self.colors['bg'], 
                                                   fg=self.colors['text'],
                                                   font=("Segoe UI", 11),
                                                   insertbackground=self.colors['accent'],
                                                   relief='flat', bd=0)
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.chat_area.config(state=tk.DISABLED)
        
        # Нижняя панель
        input_frame = tk.Frame(center_panel, bg=self.colors['bg'])
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.message_entry = tk.Entry(input_frame, font=("Segoe UI", 11),
                                      bg=self.colors['input'], fg=self.colors['text'],
                                      relief='flat', insertbackground=self.colors['accent'])
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, 
                                padx=(0, 10), ipady=8)
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
        send_btn = tk.Button(input_frame, text="Отправить", command=self.send_message,
                            bg=self.colors['accent'], fg='white',
                            font=("Segoe UI", 11, "bold"), padx=20,
                            relief='flat', cursor='hand2')
        send_btn.pack(side=tk.RIGHT)
        
        # Правая панель
        right_panel = tk.Frame(main_container, width=220, bg=self.colors['sidebar'])
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        header_right = tk.Frame(right_panel, bg=self.colors['header'], height=60)
        header_right.pack(fill=tk.X)
        header_right.pack_propagate(False)
        
        tk.Label(header_right, text="👥 УЧАСТНИКИ", font=("Segoe UI", 12, "bold"),
                bg=self.colors['header'], fg=self.colors['text']).pack(pady=15)
        
        users_frame = tk.Frame(right_panel, bg=self.colors['sidebar'])
        users_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        users_scroll = tk.Scrollbar(users_frame, bg=self.colors['sidebar'])
        users_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.users_listbox = tk.Listbox(users_frame, bg=self.colors['sidebar'],
                                        fg=self.colors['text'], font=("Segoe UI", 10),
                                        selectbackground=self.colors['accent'],
                                        relief='flat', bd=0,
                                        yscrollcommand=users_scroll.set)
        self.users_listbox.pack(fill=tk.BOTH, expand=True)
        users_scroll.config(command=self.users_listbox.yview)
        
        # Приветственное сообщение
        self.add_system_message(f"Добро пожаловать в чат, {self.name}!")
        
        # Запрашиваем данные
        self.get_rooms()
        self.get_users()
    
    def receive_messages(self):
        """Прием сообщений - ЭТА ФУНКЦИЯ КЛЮЧЕВАЯ ДЛЯ ОТОБРАЖЕНИЯ СООБЩЕНИЙ"""
        while self.running:
            try:
                # Получаем данные от сервера
                data = self.client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                print(f"Получено: {data}")  # Отладка в терминале
                
                message = json.loads(data)
                
                # Обрабатываем разные типы сообщений
                if message['type'] == 'message':
                    # Это обычное сообщение от пользователя
                    self.window.after(0, lambda: self.display_message(
                        message['name'], 
                        message['text'], 
                        message['timestamp']
                    ))
                elif message['type'] == 'system':
                    # Это системное сообщение
                    self.window.after(0, lambda: self.display_system_message(message['text']))
                elif message['type'] == 'users':
                    # Обновляем список пользователей
                    self.window.after(0, lambda: self.update_users_list(message['users']))
                elif message['type'] == 'rooms':
                    # Обновляем список комнат
                    self.window.after(0, lambda: self.update_rooms_list(message['rooms']))
                    
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}")
                continue
            except Exception as e:
                print(f"Ошибка приема: {e}")
                break
        
        if self.running:
            self.window.after(0, self.connection_lost)
    
    def display_message(self, name, text, timestamp):
        """Отображение сообщения в чате"""
        self.chat_area.config(state=tk.NORMAL)
        
        # Вставляем время
        self.chat_area.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Вставляем имя
        if name == self.name:
            self.chat_area.insert(tk.END, f"{name} (Вы): ", 'my_name')
        else:
            self.chat_area.insert(tk.END, f"{name}: ", 'other_name')
        
        # Вставляем текст
        self.chat_area.insert(tk.END, f"{text}\n", 'message')
        
        # Настраиваем стили
        self.chat_area.tag_config('timestamp', foreground='#888888', font=("Segoe UI", 9))
        self.chat_area.tag_config('my_name', foreground='#00ff00', font=("Segoe UI", 11, "bold"))
        self.chat_area.tag_config('other_name', foreground=self.colors['accent'], font=("Segoe UI", 11, "bold"))
        self.chat_area.tag_config('message', foreground=self.colors['text'], font=("Segoe UI", 11))
        
        # Прокручиваем вниз
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)
    
    def display_system_message(self, text):
        """Отображение системного сообщения"""
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"ℹ️ {text}\n", 'system')
        self.chat_area.tag_config('system', foreground='#ffaa00', font=("Segoe UI", 10, "italic"))
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)
    
    def send_message(self):
        """Отправка сообщения"""
        message = self.message_entry.get().strip()
        if message:
            try:
                data = json.dumps({'type': 'message', 'text': message})
                self.client_socket.send(data.encode('utf-8'))
                self.message_entry.delete(0, tk.END)
                print(f"Отправлено: {message}")  # Отладка
            except Exception as e:
                print(f"Ошибка отправки: {e}")
                self.display_system_message("Ошибка отправки сообщения")
    
    def join_room(self, event):
        """Присоединение к комнате"""
        selection = self.rooms_listbox.curselection()
        if selection:
            room = self.rooms_listbox.get(selection[0])
            if room != self.current_room:
                self.current_room = room
                self.room_label.config(text=room)
                data = json.dumps({'type': 'join_room', 'room': room})
                try:
                    self.client_socket.send(data.encode('utf-8'))
                    # Очищаем чат
                    self.chat_area.config(state=tk.NORMAL)
                    self.chat_area.delete(1.0, tk.END)
                    self.chat_area.config(state=tk.DISABLED)
                    self.get_users()
                except:
                    pass
    
    def create_room(self):
        """Создание комнаты"""
        room_name = self.new_room_entry.get().strip()
        if room_name:
            data = json.dumps({'type': 'create_room', 'room': room_name})
            try:
                self.client_socket.send(data.encode('utf-8'))
                self.new_room_entry.delete(0, tk.END)
            except:
                pass
    
    def get_rooms(self):
        """Получение списка комнат"""
        if hasattr(self, 'client_socket') and self.client_socket:
            try:
                data = json.dumps({'type': 'get_rooms'})
                self.client_socket.send(data.encode('utf-8'))
            except:
                pass
    
    def get_users(self):
        """Получение списка пользователей"""
        if hasattr(self, 'client_socket') and self.client_socket:
            try:
                data = json.dumps({'type': 'get_users'})
                self.client_socket.send(data.encode('utf-8'))
            except:
                pass
    
    def update_users_list(self, users):
        """Обновление списка пользователей"""
        self.users_listbox.delete(0, tk.END)
        for user in users:
            if user == self.name:
                self.users_listbox.insert(tk.END, f"● {user}")
            else:
                self.users_listbox.insert(tk.END, f"○ {user}")
    
    def update_rooms_list(self, rooms):
        """Обновление списка комнат"""
        self.rooms_listbox.delete(0, tk.END)
        for room in rooms:
            if room == self.current_room:
                self.rooms_listbox.insert(tk.END, f"📌 {room}")
            else:
                self.rooms_listbox.insert(tk.END, f"📁 {room}")
    
    def connection_lost(self):
        """Обработка потери соединения"""
        self.running = False
        messagebox.showerror("Ошибка", "Соединение с сервером потеряно!")
        self.create_login_ui()
    
    def add_system_message(self, text):
        """Добавление системного сообщения (алиас)"""
        self.display_system_message(text)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    client = ModernChatClient()
    client.run()
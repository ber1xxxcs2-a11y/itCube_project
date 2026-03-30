import customtkinter as ctk
import json
import random
import time
from tkinter import filedialog, messagebox

# Настройки внешнего вида
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Обновленный базовый пак вопросов (добавлены легкие вопросы на 10 баллов)
DEFAULT_PACK = [
    {"question": "Сколько пальцев на одной руке человека?", "options": ["4", "5", "6", "10"], "answer": "5", "max_points": 10, "time_limit": 5},
    {"question": "Какого цвета небо в ясную погоду?", "options": ["Зеленое", "Красное", "Синее", "Желтое"], "answer": "Синее", "max_points": 10, "time_limit": 5},
    {"question": "Кто создал язык программирования Python?", "options": ["Билл Гейтс", "Илон Маск", "Гвидо ван Россум", "Стив Джобс"], "answer": "Гвидо ван Россум", "max_points": 100, "time_limit": 15},
    {"question": "Какая планета самая большая в Солнечной системе?", "options": ["Земля", "Марс", "Юпитер", "Сатурн"], "answer": "Юпитер", "max_points": 50, "time_limit": 10},
    {"question": "Столица Австралии?", "options": ["Сидней", "Мельбурн", "Канберра", "Перт"], "answer": "Канберра", "max_points": 100, "time_limit": 10},
    {"question": "Сколько бит в одном байте?", "options": ["4", "8", "16", "32"], "answer": "8", "max_points": 50, "time_limit": 5},
    {"question": "Самая глубокая точка на Земле?", "options": ["Марианская впадина", "Желоб Тонга", "Филиппинский желоб", "Кермадек"], "answer": "Марианская впадина", "max_points": 50, "time_limit": 10},
    {"question": "В каком году произошел релиз первой версии Python?", "options": ["1989", "1991", "1995", "2000"], "answer": "1991", "max_points": 100, "time_limit": 15},
    {"question": "Химический символ золота?", "options": ["Ag", "Au", "Fe", "Cu"], "answer": "Au", "max_points": 50, "time_limit": 8},
    {"question": "Как называется результат сложения?", "options": ["Разность", "Произведение", "Сумма", "Частное"], "answer": "Сумма", "max_points": 50, "time_limit": 5},
    {"question": "Какой океан самый большой?", "options": ["Атлантический", "Индийский", "Тихий", "Северный Ледовитый"], "answer": "Тихий", "max_points": 50, "time_limit": 10},
    {"question": "Что из этого НЕ является языком программирования?", "options": ["HTML", "Java", "C++", "Ruby"], "answer": "HTML", "max_points": 100, "time_limit": 10}
]

class QuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Квиз: Время - Баллы!")
        self.geometry("800x650")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.questions = []
        self.current_q_index = 0
        self.score = 0
        
        # Переменные для таймера
        self.start_time = 0
        self.current_time_limit = 0
        self.current_max_points = 0
        self.timer_job = None

        self.show_main_menu()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_window()
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(frame, text="Добро пожаловать в Квиз!", font=("Helvetica", 36, "bold"))
        title.pack(pady=(60, 30))

        # --- БЛОК ВЫБОРА СЛОЖНОСТИ ---
        diff_label = ctk.CTkLabel(frame, text="Выберите сложность вопросов:", font=("Helvetica", 16))
        diff_label.pack(pady=(10, 5))
        
        self.difficulty_var = ctk.StringVar(value="Все")
        self.diff_segmented = ctk.CTkSegmentedButton(
            frame, 
            values=["Все", "10 баллов", "50 баллов", "100 баллов"], 
            variable=self.difficulty_var,
            font=("Helvetica", 14),
            width=300
        )
        self.diff_segmented.pack(pady=(0, 30))
        # -----------------------------

        btn_start_default = ctk.CTkButton(frame, text="Играть (Базовый пак)", font=("Helvetica", 18), width=300, height=50, command=lambda: self.start_game(DEFAULT_PACK))
        btn_start_default.pack(pady=10)

        btn_load_pack = ctk.CTkButton(frame, text="Загрузить свой пак (JSON)", font=("Helvetica", 18), width=300, height=50, fg_color="#2b7a5e", hover_color="#1d5440", command=self.load_custom_pack)
        btn_load_pack.pack(pady=10)

        btn_exit = ctk.CTkButton(frame, text="Выход", font=("Helvetica", 18), width=300, height=50, fg_color="#b83b3b", hover_color="#8a2c2c", command=self.quit)
        btn_exit.pack(pady=10)

    def load_custom_pack(self):
        filepath = filedialog.askopenfilename(title="Выберите пак вопросов", filetypes=[("JSON Files", "*.json")])
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    custom_pack = json.load(file)
                    self.start_game(custom_pack)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

    def start_game(self, pack):
        selected_diff = self.difficulty_var.get()
        filtered_pack = pack
        
        # Фильтруем вопросы, если выбрано что-то кроме "Все"
        if selected_diff != "Все":
            target_points = int(selected_diff.split()[0]) # Достаем число (10, 50 или 100) из строки
            filtered_pack = [q for q in pack if q.get("max_points") == target_points]
            
        if not filtered_pack:
            messagebox.showwarning("Внимание", f"В этом паке нет вопросов категории: {selected_diff}!")
            return

        # Берем до 10 случайных вопросов из отфильтрованного списка
        self.questions = random.sample(filtered_pack, min(len(filtered_pack), 10)) 
        self.current_q_index = 0
        self.score = 0
        self.show_game_screen()
        self.load_question()

    def show_game_screen(self):
        self.clear_window()

        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=20)

        self.score_label = ctk.CTkLabel(self.top_frame, text="Счет: 0", font=("Helvetica", 20, "bold"))
        self.score_label.pack(side="left")

        self.timer_label = ctk.CTkLabel(self.top_frame, text="Время: 0.0с", font=("Helvetica", 20, "bold"), text_color="#d64d4d")
        self.timer_label.pack(side="right")

        self.points_potential_label = ctk.CTkLabel(self.top_frame, text="Текущий балл: 0", font=("Helvetica", 20))
        self.points_potential_label.pack(side="right", padx=30)

        self.progress_bar = ctk.CTkProgressBar(self, width=600)
        self.progress_bar.pack(pady=(0, 20))
        self.progress_bar.set(1)

        self.card_frame = ctk.CTkFrame(self, corner_radius=20)
        self.card_frame.pack(expand=True, fill="both", padx=40, pady=(0, 40))

        self.question_label = ctk.CTkLabel(self.card_frame, text="Вопрос", font=("Helvetica", 24, "bold"), wraplength=600)
        self.question_label.pack(pady=40, padx=20)

        self.buttons_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.buttons_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        self.buttons_frame.grid_columnconfigure((0, 1), weight=1, uniform="group1")
        self.buttons_frame.grid_rowconfigure((0, 1), weight=1, uniform="group1")

        self.option_buttons = []
        for i in range(4):
            btn = ctk.CTkButton(self.buttons_frame, text="", font=("Helvetica", 18), height=80, corner_radius=15)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            self.option_buttons.append(btn)

    def load_question(self):
        if self.current_q_index >= len(self.questions):
            self.end_game()
            return

        q_data = self.questions[self.current_q_index]
        self.question_label.configure(text=f"[{q_data['max_points']} очков] {q_data['question']}")
        
        options = q_data["options"].copy()
        random.shuffle(options)

        for i, btn in enumerate(self.option_buttons):
            btn.configure(
                text=options[i], 
                state="normal", 
                fg_color=["#3a7ebf", "#1f538d"],
                command=lambda ans=options[i]: self.check_answer(ans)
            )

        self.current_time_limit = q_data["time_limit"]
        self.current_max_points = q_data["max_points"]
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        elapsed = time.time() - self.start_time
        time_left = self.current_time_limit - elapsed

        if time_left <= 0:
            time_left = 0
            self.timer_label.configure(text="Время: 0.0с")
            self.progress_bar.set(0)
            self.points_potential_label.configure(text="Текущий балл: 0")
            self.check_answer(None)
            return

        current_points = int(self.current_max_points * (time_left / self.current_time_limit))
        
        self.timer_label.configure(text=f"Время: {time_left:.1f}с")
        self.points_potential_label.configure(text=f"Возможный балл: {current_points}")
        self.progress_bar.set(time_left / self.current_time_limit)

        self.timer_job = self.after(50, self.update_timer)

    def check_answer(self, selected_answer):
        if self.timer_job:
            self.after_cancel(self.timer_job)

        q_data = self.questions[self.current_q_index]
        correct_answer = q_data["answer"]

        elapsed = time.time() - self.start_time
        if selected_answer == correct_answer:
            points_earned = max(1, int(self.current_max_points * ((self.current_time_limit - elapsed) / self.current_time_limit)))
            self.score += points_earned
            self.score_label.configure(text=f"Счет: {self.score}")
        else:
            points_earned = 0

        for btn in self.option_buttons:
            btn.configure(state="disabled")
            if btn.cget("text") == correct_answer:
                btn.configure(fg_color="#2b7a5e")
            elif btn.cget("text") == selected_answer:
                btn.configure(fg_color="#b83b3b")

        self.current_q_index += 1
        self.after(1500, self.load_question)

    def end_game(self):
        self.clear_window()
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True)

        title = ctk.CTkLabel(frame, text="Игра окончена!", font=("Helvetica", 40, "bold"))
        title.pack(pady=20)

        score_lbl = ctk.CTkLabel(frame, text=f"Твой итоговый счет: {self.score}", font=("Helvetica", 28))
        score_lbl.pack(pady=20)

        btn_menu = ctk.CTkButton(frame, text="В главное меню", font=("Helvetica", 18), width=250, height=50, command=self.show_main_menu)
        btn_menu.pack(pady=30)

app = QuizApp()
app.mainloop()
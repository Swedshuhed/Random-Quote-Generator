import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

DATA_FILE = "quotes_history.json"

class QuoteGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("700x600")

        # Предопределенные цитаты
        self.predefined_quotes = [
            {"text": "Будьте сами собой, все остальные роли уже заняты.", "author": "Оскар Уайльд", "topic": "Жизнь"},
            {"text": "Жизнь — это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон", "topic": "Жизнь"},
            {"text": "Сложнее всего начать действовать, все остальное зависит только от упорства.", "author": "Амелия Эрхарт", "topic": "Мотивация"},
            {"text": "Логика приведет вас из пункта А в пункт Б. Воображение приведет вас куда угодно.", "author": "Альберт Эйнштейн", "topic": "Творчество"},
            {"text": "Не относитесь к жизни слишком серьезно. Вам все равно не уйти из нее живыми.", "author": "Элберт Хаббард", "topic": "Юмор"},
            {"text": "Программирование — это разбиение чего-то большого и невозможного на что-то маленькое и реальное.", "author": "Неизвестный", "topic": "Программирование"}
        ]

        # Данные приложения
        self.all_quotes = self.predefined_quotes.copy()
        self.history = []  # Хранит индексы или объекты цитат из истории

        # Списки для фильтрации
        self.authors = sorted(list(set(q["author"] for q in self.all_quotes)))
        self.topics = sorted(list(set(q["topic"] for q in self.all_quotes)))

        self.load_history()
        self.setup_ui()
        self.update_filter_lists()

    def setup_ui(self):
        # --- Блок управления (слева) ---
        control_frame = ttk.LabelFrame(self.root, text="Управление", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Button(control_frame, text="🎲 Сгенерировать цитату", command=self.generate_quote).pack(pady=5, fill=tk.X)

        # Добавление новой цитаты
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(control_frame, text="Добавить новую цитату:").pack(anchor=tk.W)
        
        self.new_text = tk.Text(control_frame, height=3, width=30)
        self.new_text.pack(pady=2)
        ttk.Label(control_frame, text="Автор:").pack(anchor=tk.W)
        self.new_author = ttk.Entry(control_frame, width=30)
        self.new_author.pack(pady=2)
        ttk.Label(control_frame, text="Тема:").pack(anchor=tk.W)
        self.new_topic = ttk.Entry(control_frame, width=30)
        self.new_topic.pack(pady=2)
        
        ttk.Button(control_frame, text="➕ Добавить цитату", command=self.add_new_quote).pack(pady=5)

        # Фильтры
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(control_frame, text="Фильтр по автору:").pack(anchor=tk.W)
        self.author_filter = ttk.Combobox(control_frame, values=["Все"] + self.authors, state="readonly")
        self.author_filter.set("Все")
        self.author_filter.pack(pady=2, fill=tk.X)
        self.author_filter.bind("<<ComboboxSelected>>", self.apply_filters)

        ttk.Label(control_frame, text="Фильтр по теме:").pack(anchor=tk.W)
        self.topic_filter = ttk.Combobox(control_frame, values=["Все"] + self.topics, state="readonly")
        self.topic_filter.set("Все")
        self.topic_filter.pack(pady=2, fill=tk.X)
        self.topic_filter.bind("<<ComboboxSelected>>", self.apply_filters)

        ttk.Button(control_frame, text="🔄 Сбросить фильтры", command=self.reset_filters).pack(pady=5, fill=tk.X)

        # --- Блок отображения (справа) ---
        display_frame = ttk.LabelFrame(self.root, text="Цитаты", padding=10)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Текущая сгенерированная цитата
        self.current_quote_label = tk.Message(display_frame, text="Нажмите 'Сгенерировать'", 
                                              font=("Arial", 12), width=400, relief=tk.SUNKEN, bg="white")
        self.current_quote_label.pack(pady=10, fill=tk.X)

        # История (с прокруткой)
        ttk.Label(display_frame, text="История:").pack(anchor=tk.W)
        list_frame = ttk.Frame(display_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                          font=("Arial", 10), activestyle='none')
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)

    def generate_quote(self):
        if not self.all_quotes:
            messagebox.showwarning("Внимание", "Нет доступных цитат для генерации.")
            return

        # Применяем фильтры
        filtered = self.get_filtered_quotes()
        if not filtered:
            messagebox.showinfo("Фильтр", "Нет цитат, соответствующих фильтрам.")
            return

        quote = random.choice(filtered)
        display_text = f"«{quote['text']}»\n\n— {quote['author']} ({quote['topic']})"
        self.current_quote_label.config(text=display_text)

        # Добавляем в историю
        self.history.append(quote)
        self.update_history_display()
        self.save_history()

    def add_new_quote(self):
        text = self.new_text.get("1.0", tk.END).strip()
        author = self.new_author.get().strip()
        topic = self.new_topic.get().strip()

        # Проверка на пустые строки
        if not text or not author or not topic:
            messagebox.showerror("Ошибка", "Все поля (цитата, автор, тема) должны быть заполнены.")
            return

        new_quote = {"text": text, "author": author, "topic": topic}
        self.all_quotes.append(new_quote)
        
        # Обновляем списки для фильтров
        if author not in self.authors:
            self.authors.append(author)
            self.authors.sort()
        if topic not in self.topics:
            self.topics.append(topic)
            self.topics.sort()
        
        self.update_filter_lists()
        
        # Очистка полей
        self.new_text.delete("1.0", tk.END)
        self.new_author.delete(0, tk.END)
        self.new_topic.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Новая цитата добавлена в коллекцию!")

    def get_filtered_quotes(self):
        author_sel = self.author_filter.get()
        topic_sel = self.topic_filter.get()
        
        filtered = self.all_quotes
        if author_sel != "Все":
            filtered = [q for q in filtered if q["author"] == author_sel]
        if topic_sel != "Все":
            filtered = [q for q in filtered if q["topic"] == topic_sel]
        return filtered

    def apply_filters(self, event=None):
        self.update_history_display()  # Обновляем отображение истории в соответствии с фильтром

    def reset_filters(self):
        self.author_filter.set("Все")
        self.topic_filter.set("Все")
        self.update_history_display()

    def update_history_display(self):
        self.history_listbox.delete(0, tk.END)
        filtered_history = self.get_filtered_quotes()
        # Показываем только те цитаты из истории, которые прошли фильтр
        history_ids = {id(q): q for q in self.history}
        filtered_history_ids = {id(q): q for q in filtered_history}
        
        items_to_show = []
        for q in self.history:
            if id(q) in filtered_history_ids:
                items_to_show.append(f"«{q['text'][:30]}...» — {q['author']}")
        
        for item in items_to_show:
            self.history_listbox.insert(tk.END, item)

    def update_filter_lists(self):
        self.author_filter['values'] = ["Все"] + self.authors
        self.topic_filter['values'] = ["Все"] + self.topics

    def save_history(self):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения истории: {e}")

    def load_history(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # Добавляем загруженные цитаты в all_quotes, если их там нет
                for q in loaded:
                    if q not in self.all_quotes:
                        self.all_quotes.append(q)
                self.history = loaded
                self.update_history_display()
        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGeneratorApp(root)
    root.mainloop()

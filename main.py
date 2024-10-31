import pymysql
import tkinter as tk
from tkinter import messagebox, Scrollbar, ttk
import json
import os
import sys

def load_config():
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
            if not all(key in config for key in ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]):
                return {
                    "DB_HOST": "",
                    "DB_USER": "",
                    "DB_PASSWORD": "",
                    "DB_NAME": ""
                }
            return config
    except (FileNotFoundError, ValueError):
        return {
            "DB_HOST": "",
            "DB_USER": "",
            "DB_PASSWORD": "",
            "DB_NAME": ""
        }

def save_config(host, user, password, db_name):
    config = {
        "DB_HOST": host,
        "DB_USER": user,
        "DB_PASSWORD": password,
        "DB_NAME": db_name
    }
    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)

config = load_config()

def connect_to_database():
    global conn
    try:
        conn = pymysql.connect(
            host=config["DB_HOST"],
            user=config["DB_USER"],
            password=config["DB_PASSWORD"],
            database=config["DB_NAME"]
        )
        return True
    except pymysql.MySQLError:
        return False

def check_connection():
    try:
        conn.ping(reconnect=True)
    except pymysql.MySQLError:
        messagebox.showerror("Ошибка подключения", "Разорвано соединение к MySQL.\nПожалуйста, проверьте подключение.")

def execute_command():
    if not all([config["DB_HOST"], config["DB_USER"], config["DB_PASSWORD"], config["DB_NAME"]]):
        messagebox.showwarning("Пустая конфигурация", "Конфигурация подключения пуста.\nПожалуйста, настройте ее в окне настроек.")
        return

    if not connect_to_database():
        messagebox.showerror("Ошибка подключения к MySQL", "Не удалось подключиться к базе данных.\nПожалуйста, проверьте настройки подключения.")
        return

    check_connection()
    command = text_box.get("1.0", tk.END).strip()

    if not command:
        messagebox.showerror("Ошибка", "Неверная команда.\nПожалуйста, введите команду.")
        return

    confirmation = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите\nвыполнить команду?")
    if confirmation:
        try:
            print("Executing command:", command)
            with conn.cursor() as cursor:
                cursor.execute(command)
                conn.commit()
                messagebox.showinfo("Успех", "Команда успешно выполнена.")
        except pymysql.MySQLError as e:
            error_message = f"Ошибка выполнения команды:\n{e.args[0]} - {e.args[1]}"
            messagebox.showerror("Ошибка выполнения", error_message)

def paste_from_clipboard():
    try:
        clipboard_text = root.clipboard_get()
        text_box.insert(tk.END, clipboard_text)
    except tk.TclError:
        messagebox.showwarning("Ошибка", "Буфер обмена пуст.\nПожалуйста, скопируйте текст перед вставкой.")

def clear_text_box():
    text_box.delete("1.0", tk.END)

def open_settings_window():
    settings_window = tk.Toplevel(root)
    settings_window.title("Настройки")
    settings_window.geometry("650x730")

    tk.Label(settings_window, text="Хост базы данных:").pack(pady=10)
    host_entry = tk.Entry(settings_window, width=50)
    host_entry.insert(0, config["DB_HOST"])
    host_entry.pack(pady=10)

    tk.Label(settings_window, text="Пользователь:").pack(pady=10)
    user_entry = tk.Entry(settings_window, width=50)
    user_entry.insert(0, config["DB_USER"])
    user_entry.pack(pady=10)

    tk.Label(settings_window, text="Пароль:").pack(pady=10)
    password_entry = tk.Entry(settings_window, width=50, show="*")
    password_entry.insert(0, config["DB_PASSWORD"])
    password_entry.pack(pady=10)

    tk.Label(settings_window, text="Имя базы данных:").pack(pady=10)
    db_name_entry = tk.Entry(settings_window, width=50)
    db_name_entry.insert(0, config["DB_NAME"])
    db_name_entry.pack(pady=10)

    def save_settings():
        host = host_entry.get()
        user = user_entry.get()
        password = password_entry.get()
        db_name = db_name_entry.get()
        save_config(host, user, password, db_name)

        print("[INFO] Программа была закрыта для сохранения данных, откройте программу вновь.", file=sys.stderr)
        os._exit(0)

    save_button = ttk.Button(settings_window, text="Сохранить", command=save_settings)
    save_button.pack(pady=20)

root = tk.Tk()
root.title("SQL Executor")
root.geometry("500x400")
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", padding=6, relief="flat", background="#4CAF50", foreground="white")
style.configure("TLabel", background="#f2f2f2", font=("Arial", 10))
style.configure("TText", background="#ffffff", font=("Arial", 10))
style.map("TButton", background=[("active", "#45a049")])

label = tk.Label(root, text="Введите команду:", font=("Arial", 10))
label.grid(row=0, column=0, pady=(10, 5), padx=10, sticky="w")

frame = tk.Frame(root)
frame.grid(row=1, column=0, pady=5, padx=10, sticky="nsew")

text_box = tk.Text(frame, height=10, wrap=tk.WORD, font=("Arial", 10))
scrollbar = Scrollbar(frame, command=text_box.yview)
text_box.config(yscrollcommand=scrollbar.set)

text_box.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)

paste_button = ttk.Button(root, text="Вставить", command=paste_from_clipboard, width=15)
paste_button.grid(row=2, column=0, pady=(5, 0), sticky="ew")

clear_button = ttk.Button(root, text="Очистить", command=clear_text_box, width=15)
clear_button.grid(row=3, column=0, pady=(5, 0), sticky="ew")

execute_button = ttk.Button(root, text="Выполнить", command=execute_command, width=15)
execute_button.grid(row=4, column=0, pady=(10, 10), sticky="ew")

settings_button = ttk.Button(root, text="Настройки", command=open_settings_window, width=15)
settings_button.grid(row=5, column=0, pady=(5, 0), sticky="ew")

root.mainloop()

if 'conn' in locals():
    conn.close()
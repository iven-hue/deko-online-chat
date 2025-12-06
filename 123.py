import base64
import io
import threading
from socket import socket, AF_INET, SOCK_STREAM

from customtkinter import *
from tkinter import filedialog
from PIL import Image


class MainWindow(CTk):
    def __init__(self):
        super().__init__()

        self.geometry('400x300')
        self.title("Chat Client")

        self.username = "Artem"

        # Меню
        self.label = None
        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.speed_animate_menu = -20
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)

        # Основне поле чату
        self.chat_field = CTkScrollableFrame(self, width=300, height=200)
        self.chat_field.place(x=0, y=0)

        # Поле введення + кнопки
        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', width=250, height=40)
        self.message_entry.place(x=30, y=260)

        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
        self.send_button.place(x=310, y=260)

        self.open_img_button = CTkButton(self, text='📂', width=50, height=40, command=self.open_image)
        self.open_img_button.place(x=250, y=260)

        self.adaptive_ui()

        try:
            self.add_message("Демонстрація відображення зображення:",
                             CTkImage(Image.open('Screenshot_1.png'), size=(300, 300)))
        except:
            pass

        # Подключение к Ngrok с новым портом
        try:
            SERVER_HOST = "0.tcp.jp.ngrok.io"
            SERVER_PORT = 16881

            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((SERVER_HOST, SERVER_PORT))

            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався до чату!"
            self.sock.send(hello.encode('utf-8'))

            threading.Thread(target=self.recv_message, daemon=True).start()

        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

    # Меню
    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()

            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=30)

            self.entry = CTkEntry(self.menu_frame, placeholder_text="Ваш нік...")
            self.entry.pack()

            self.save_button = CTkButton(self.menu_frame, text="Зберегти", command=self.save_name)
            self.save_button.pack()

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)

        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 60 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label:
                self.label.destroy()
            if getattr(self, "entry", None):
                self.entry.destroy()
            if getattr(self, "save_button", None):
                self.save_button.destroy()

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_message(f"Ваш новий нік: {self.username}")

    # Адаптивный UI
    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())

        self.chat_field.place(x=self.menu_frame.winfo_width(), y=0)
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20,
                                  height=self.winfo_height() - 60)

        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.winfo_height() - 40)
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.open_img_button.place(x=self.winfo_width() - 100, y=self.winfo_height() - 40)

        self.after(100, self.adaptive_ui)

    # Добавление сообщений
    def add_message(self, text, image=None):
        frame = CTkFrame(self.chat_field)
        frame.pack(anchor='w', pady=5, padx=5)

        CTkLabel(frame, text=text).pack(anchor='w')

        if image:
            CTkLabel(frame, image=image, text="").pack(anchor='w')

    # Отправка текста
    def send_message(self):
        msg = self.message_entry.get().strip()
        if not msg:
            return

        full = f"TEXT@{self.username}@{msg}"
        try:
            self.sock.send(full.encode('utf-8'))
        except:
            self.add_message("Не вдалося відправити повідомлення")

        self.message_entry.delete(0, "end")

    # Отправка изображения
    def open_image(self):
        file = filedialog.askopenfilename()
        if not file:
            return

        img = Image.open(file)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        full = f"IMG@{self.username}@{b64}"
        try:
            self.sock.send(full.encode('utf-8'))
        except:
            self.add_message("Не вдалося відправити зображення")

    # Получение сообщений
    def recv_message(self):
        while True:
            try:
                data = self.sock.recv(999999).decode('utf-8')
                if data.startswith("TEXT@"):
                    _, user, msg = data.split("@", 2)
                    self.add_message(f"{user}: {msg}")
                elif data.startswith("IMG@"):
                    _, user, b64 = data.split("@", 2)
                    raw = base64.b64decode(b64)
                    img = Image.open(io.BytesIO(raw))
                    ctk_img = CTkImage(img, size=(300, 300))
                    self.add_message(f"{user} надіслав фото:", ctk_img)
            except:
                break


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
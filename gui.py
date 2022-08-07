import asyncio
import tkinter as tk
from asyncio import Queue
from enum import Enum
from tkinter.scrolledtext import ScrolledText


class TkAppClosed(Exception):
    """Tkinter application closed."""


class ReadConnectionStateChanged(Enum):
    INITIATED = 'устанавливаем соединение'
    ESTABLISHED = 'соединение установлено'
    CLOSED = 'соединение закрыто'

    def __str__(self):
        return str(self.value)


class SendingConnectionStateChanged(Enum):
    INITIATED = 'устанавливаем соединение'
    ESTABLISHED = 'соединение установлено'
    CLOSED = 'соединение закрыто'

    def __str__(self):
        return str(self.value)


class NicknameReceived:
    def __init__(self, nickname: str):
        self.nickname = nickname


def process_new_message(input_field: tk.Entry, sending_queue: Queue):
    text = input_field.get()
    sending_queue.put_nowait(text)
    input_field.delete(0, tk.END)


async def update_tk(root_frame: tk.Frame, interval=1/120):
    while True:
        try:
            root_frame.update()
        except tk.TclError:
            raise TkAppClosed()
        await asyncio.sleep(interval)


async def update_conversation_history(panel: ScrolledText, messages_queue: Queue):
    while True:
        msg = await messages_queue.get()
        panel["state"] = tk.NORMAL

        if panel.index("end-1c") != "1.0":
            panel.insert(tk.END, "\n")

        panel.insert(tk.END, msg)
        # TODO: Сделать промотку умной, чтобы не мешала просматривать историю сообщений
        # ScrolledText.frame
        # ScrolledText.vbar
        panel.yview(tk.END)
        panel["state"] = tk.DISABLED


def write_history(panel: ScrolledText, messages: list[str]):
    panel["state"] = tk.NORMAL

    for message in messages:
        if panel.index("end-1c") != "1.0":
            panel.insert(tk.END, "\n")

        panel.insert(tk.END, message)

    panel.yview(tk.END)
    panel["state"] = tk.DISABLED


async def update_status_panel(status_labels: tuple[tk.Label, ...], status_updates_queue: Queue):
    nickname_label, read_label, write_label = status_labels

    read_label["text"] = f"Чтение: нет соединения"
    write_label["text"] = f"Отправка: нет соединения"
    nickname_label["text"] = f"Имя пользователя: неизвестно"

    while True:
        msg = await status_updates_queue.get()

        if isinstance(msg, ReadConnectionStateChanged):
            read_label["text"] = f"Чтение: {msg}"
        elif isinstance(msg, SendingConnectionStateChanged):
            write_label["text"] = f"Отправка: {msg}"
        elif isinstance(msg, NicknameReceived):
            nickname_label["text"] = f"Имя пользователя: {msg.nickname}"


def create_status_panel(root_frame: tk.Frame):
    status_frame = tk.Frame(root_frame)
    status_frame.pack(side="bottom", fill=tk.X)

    connections_frame = tk.Frame(status_frame)
    connections_frame.pack(side=tk.LEFT)

    nickname_label = tk.Label(connections_frame, height=1, fg="grey", font="arial 10", anchor=tk.W)
    nickname_label.pack(side=tk.TOP, fill=tk.X)

    status_read_label = tk.Label(connections_frame, height=1, fg="grey", font="arial 10", anchor=tk.W)
    status_read_label.pack(side=tk.TOP, fill=tk.X)

    status_write_label = tk.Label(connections_frame, height=1, fg="grey", font="arial 10", anchor=tk.W)
    status_write_label.pack(side=tk.TOP, fill=tk.X)

    return nickname_label, status_read_label, status_write_label


async def draw(history: list[str], messages_queue: Queue, sending_queue: Queue, status_updates_queue: Queue):
    root = tk.Tk()
    root.title("Чат майнкрафтера")

    root_frame = tk.Frame()
    root_frame.pack(fill=tk.BOTH, expand=True)

    status_labels = create_status_panel(root_frame)

    input_frame = tk.Frame(root_frame)
    input_frame.pack(side=tk.BOTTOM, fill=tk.X)

    input_field = tk.Entry(input_frame)
    input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
    input_field.bind("<Return>", lambda event: process_new_message(input_field, sending_queue))

    send_button = tk.Button(
        input_field,
        text="Отправить",
        command=lambda: process_new_message(input_field, sending_queue)
    )
    send_button.pack(side="right")

    conversation_panel = ScrolledText(root_frame, wrap="none")  # wrap - перенос слов
    conversation_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    write_history(conversation_panel, history)

    await asyncio.gather(
        update_tk(root_frame),
        update_conversation_history(conversation_panel, messages_queue),
        update_status_panel(status_labels, status_updates_queue),
    )

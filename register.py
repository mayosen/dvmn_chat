import json
import logging
import tkinter as tk
from argparse import ArgumentParser
from os import environ
from tkinter import messagebox

from utils import encode, open_socket, decode

logger = logging.getLogger("register")
PLUG = encode("")


def parse_config():
    parser = ArgumentParser()
    parser.add_argument("--host", type=str, help="Server host")
    parser.add_argument("--port", type=int, help="Server send port")
    args = parser.parse_args()

    host = args.host or environ.get("SERVER_HOST", "minechat.dvmn.org")
    port = args.port or environ.get("PORT", 5050)

    return host, port


def register(nickname_field: tk.Entry, root: tk.Frame, host: str, port: int):
    nickname = nickname_field.get()
    nickname_field.delete(0, tk.END)

    if not nickname:
        logger.error("Empty nickname")
        messagebox.showwarning("Пустой никнейм", "Повторите ввод")
        return

    with open_socket(host, port) as socket:
        message = decode(socket.receive())
        logger.debug("message: '%s'", message)
        socket.sendall(PLUG)
        message = decode(socket.receive())
        logger.debug("message: '%s'", message)
        socket.sendall(encode(nickname))
        message = decode(socket.receive())
        logger.debug("message: '%s'", message)
        data = message.split("\n")[0]
        credentials = json.loads(data)

    path = "credentials.json"
    with open(path, "w") as file:
        json.dump(credentials, file, indent=4)

    messagebox.showinfo("Успешно", f"Учетные данные сохранены в файл {path}.")
    logger.debug("Successfully shutting down")
    root.quit()


def main():
    host, port = parse_config()

    root = tk.Tk()
    root.title("Регистрация")
    root.geometry("900x400")

    root_frame = tk.Frame()
    root_frame.pack(fill=tk.BOTH, expand=True)

    nickname_frame = tk.Frame(root_frame)
    nickname_frame.pack(side=tk.TOP, pady=25)
    nickname_label = tk.Label(nickname_frame, text="Желаемый никнейм")
    nickname_label.pack(side=tk.LEFT, fill=tk.X, pady=25, padx=25)
    nickname_field = tk.Entry(nickname_frame)
    nickname_field.pack(side=tk.RIGHT, fill=tk.X)

    submit_button = tk.Button(
        root_frame,
        text="Зарегистрироваться",
        command=lambda: register(nickname_field, root_frame, host, port)
    )
    submit_button.pack(side=tk.TOP)

    root_frame.mainloop()


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s.%(msecs).03d] %(levelname)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )

    try:
        main()
    except (tk.TclError, KeyboardInterrupt):
        logger.debug("Client has been closed")

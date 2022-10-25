import json
import logging
import tkinter as tk
from tkinter import messagebox

from utils import encode, open_socket, decode

logger = logging.getLogger("register")
PLUG = encode("")


def register(nickname: str, path: str, root: tk.Frame):
    path = f"{path or '.'}/credentials.json"

    if not nickname:
        logger.error("Empty nickname")
        messagebox.showwarning("Пустой никнейм", "Повторите ввод")
        return

    with open_socket("minechat.dvmn.org", 5050) as socket:
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

    with open(path, "w") as file:
        json.dump(credentials, file, indent=4)

    messagebox.showinfo("Успешно", f"Учетные данные сохранены в {path}.")
    logger.debug("Successfully shutting down")
    root.quit()


def main():
    root = tk.Tk()
    root.title("Регистрация")
    root.geometry("1000x800")

    root_frame = tk.Frame()
    root_frame.pack(fill=tk.Y, expand=True)

    nickname_frame = tk.Frame(root_frame)
    nickname_frame.pack(side=tk.TOP)
    nickname_label = tk.Label(nickname_frame, text="Желаемый никнейм")
    nickname_label.pack(side=tk.LEFT, fill=tk.X)
    nickname_field = tk.Entry(nickname_frame)
    nickname_field.pack(side=tk.RIGHT, fill=tk.X, expand=True)

    path_frame = tk.Frame(root_frame)
    path_frame.pack(side=tk.TOP)
    path_label = tk.Label(path_frame, text="Путь для сохранения учетных данных")
    path_label.pack(side=tk.LEFT, fill=tk.X)
    path_field = tk.Entry(path_frame)
    path_field.pack(side=tk.RIGHT, fill=tk.X, expand=True)

    submit_button = tk.Button(
        root_frame,
        text="Зарегистрироваться",
        command=lambda: register(nickname_field.get(), path_field.get(), root_frame)
    )
    submit_button.pack(side=tk.BOTTOM)

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

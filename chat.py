import asyncio
import json
import logging
import os.path
from argparse import ArgumentParser
from os import environ
from asyncio import Queue
from tkinter import messagebox

import aiofiles
from async_timeout import timeout

from gui import draw, NicknameReceived, SendingConnectionStateChanged, ReadConnectionStateChanged, TkAppClosed
from utils import open_connection, decode, format_log, encode


# TODO: README


class InvalidToken(Exception):
    """Invalid account_hash."""


def parse_config():
    parser = ArgumentParser()
    parser.add_argument("--host", type=str, help="Server host")
    parser.add_argument("--listen", type=int, help="Server listen port")
    parser.add_argument("--send", type=int, help="Server send port")
    parser.add_argument("--path", type=str, help="Relative path to logs file")
    parser.add_argument("--hash", type=str, help="Account hash to access host")
    args = parser.parse_args()

    host = args.host or environ.get("SERVER_HOST", "minechat.dvmn.org")
    listen_port = args.listen or environ.get("SERVER_LISTEN_PORT", 5000)
    send_port = args.send or environ.get("SERVER_SEND_PORT", 5050)
    path = args.path or environ.get("LOG_PATH", ".")
    path.strip("/")
    user_hash = args.hash or environ.get("USER_HASH")

    return host, listen_port, send_port, path, user_hash


async def read_messages(
        host: str, port: int, messages_queue: Queue, save_queue: Queue, updates: Queue, watchdog: Queue
):
    updates.put_nowait(ReadConnectionStateChanged.INITIATED)

    async with open_connection(host, port) as (reader, writer):
        while True:
            try:
                async with timeout(1):
                    response = await reader.readline()
                    updates.put_nowait(ReadConnectionStateChanged.ESTABLISHED)
            except asyncio.TimeoutError:
                logging.warning("1s timeout is elapsed")
                updates.put_nowait(ReadConnectionStateChanged.CLOSED)
                continue

            message = decode(response)
            watchdog.put_nowait(f"Connection is alive. New message in chat")
            messages_queue.put_nowait(message)
            save_queue.put_nowait(message)


def read_history(filepath: str):
    filename = f"{filepath}/logs.txt"

    if not os.path.exists(filename):
        return []

    with open(filename, "r") as logs:
        messages = [line.rstrip("\n") for line in logs.readlines()]
        return messages


async def save_messages(filepath: str, save_queue: Queue):
    async with aiofiles.open(f"{filepath}/logs.txt", "a") as logs:
        while True:
            message = await save_queue.get()
            await logs.write(format_log(message))


async def send_messages(
        host: str, port: int, user_hash: str, sending_queue: Queue, updates: Queue, watchdog: Queue
):
    updates.put_nowait(SendingConnectionStateChanged.INITIATED)

    async with open_connection(host, port) as (reader, writer):
        # TODO: Таймауты

        updates.put_nowait(SendingConnectionStateChanged.ESTABLISHED)
        await reader.readline()  # Enter hash
        watchdog.put_nowait("Connection is alive. Prompt before auth")
        writer.write(encode(user_hash))
        await writer.drain()

        response = decode(await reader.readline())
        user_info = json.loads(response)

        if not user_info:
            raise InvalidToken

        watchdog.put_nowait("Connection is alive. Authorization done")
        updates.put_nowait(NicknameReceived(user_info["nickname"]))

        while True:
            message = await sending_queue.get()
            message = message.replace("\n", "")
            writer.write(encode(f"{message}\n"))
            watchdog.put_nowait("Connection is alive. Message sent")
            await writer.drain()


async def watch_for_connection(watchdog_queue: Queue):
    logger = logging.getLogger("watchdog_logger")

    while True:
        event = await watchdog_queue.get()
        logger.debug(event)


async def main():
    logging.basicConfig(
        format="[%(asctime)s.%(msecs).03d] %(levelname)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )
    host, listen_port, send_port, filepath, user_hash = parse_config()

    messages_queue = Queue()
    sending_queue = Queue()
    status_updates_queue = Queue()
    save_queue = Queue()
    watchdog_queue = Queue()
    history = read_history(filepath)

    try:
        await asyncio.gather(
            draw(history, messages_queue, sending_queue, status_updates_queue),
            read_messages(host, listen_port, messages_queue, save_queue, status_updates_queue, watchdog_queue),
            save_messages(filepath, save_queue),
            send_messages(host, send_port, user_hash, sending_queue, status_updates_queue, watchdog_queue),
            watch_for_connection(watchdog_queue),
        )
    except InvalidToken:
        messagebox.showwarning("Неверный токен", "Проверьте токен, сервер его не узнал")
        return
    except TkAppClosed:
        logging.debug("Клиент закрыт")
        return


if __name__ == "__main__":
    asyncio.run(main())

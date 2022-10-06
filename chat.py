import json
import logging
import os.path
from argparse import ArgumentParser
from asyncio import Queue, TimeoutError
from os import environ
from tkinter import messagebox

import aiofiles
import anyio
from async_timeout import timeout

from gui import draw, NicknameReceived, SendingConnectionStateChanged, ReadConnectionStateChanged, TkAppClosed
from utils import open_connection, decode, format_log, encode

logger = logging.getLogger("chat")
TIMEOUT = 3
PING_PONG_INTERVAL = 5
RECONNECTION_INTERVALS = (5, 10, 15, 60, 600)


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
    listen_port = args.listen or environ.get("LISTEN_PORT", 5000)
    send_port = args.send or environ.get("SEND_PORT", 5050)
    path = args.path or environ.get("LOG_PATH", ".")
    path.strip("/")
    user_hash = args.hash or environ.get("USER_HASH")

    return path, (host, listen_port, send_port, user_hash)


async def read_messages(
        host: str,
        port: int,
        messages_queue: Queue,
        save_queue: Queue,
        updates_queue: Queue,
):
    updates_queue.put_nowait(ReadConnectionStateChanged.INITIATED)
    updates_queue.put_nowait(ReadConnectionStateChanged.ESTABLISHED)

    async with open_connection(host, port) as (reader, writer):
        try:
            while True:
                async with timeout(TIMEOUT):
                    response = await reader.readline()

                message = decode(response)
                messages_queue.put_nowait(message)
                save_queue.put_nowait(message)

        except TimeoutError:
            updates_queue.put_nowait(ReadConnectionStateChanged.CLOSED)
            logger.error("Caught reading timeout")
            raise ConnectionError


async def send_messages(
        host: str,
        port: int,
        user_hash: str,
        sending_queue: Queue,
        updates_queue: Queue,
):
    updates_queue.put_nowait(SendingConnectionStateChanged.INITIATED)
    updates_queue.put_nowait(SendingConnectionStateChanged.ESTABLISHED)

    async with open_connection(host, port) as (reader, writer):
        await reader.readline()
        writer.write(encode(user_hash))
        await writer.drain()

        response = decode(await reader.readline())
        user_info = json.loads(response)

        if not user_info:
            raise InvalidToken

        updates_queue.put_nowait(NicknameReceived(user_info["nickname"]))

        while True:
            message = await sending_queue.get()
            message = message.replace("\n", "")
            writer.write(encode(f"{message}\n"))
            await writer.drain()


async def watch_for_sending(host: str, port: int, user_hash: str, updates_queue: Queue):
    plug = encode("\n")

    async with open_connection(host, port) as (reader, writer):
        await reader.readline()
        writer.write(encode(user_hash))
        await writer.drain()
        await reader.readline()
        await reader.readline()

        try:
            while True:
                writer.write(plug)
                await writer.drain()

                async with timeout(TIMEOUT):
                    await reader.readline()

                await anyio.sleep(PING_PONG_INTERVAL)

        except TimeoutError:
            logger.error("Caught sending timeout")
            updates_queue.put_nowait(SendingConnectionStateChanged.CLOSED)
            raise ConnectionError


async def save_messages(filepath: str, save_queue: Queue):
    async with aiofiles.open(f"{filepath}/logs.txt", "a") as logs:
        while True:
            message = await save_queue.get()
            await logs.write(format_log(message))


def read_history(filepath: str):
    filename = f"{filepath}/logs.txt"

    if not os.path.exists(filename):
        return []

    with open(filename, "r") as logs:
        messages = [line.rstrip("\n") for line in logs.readlines()]
        return messages


async def handle_connection(
        config: tuple[str, int, int, str],
        messages_queue: Queue,
        sending_queue: Queue,
        updates_queue: Queue,
        save_queue: Queue,
):
    host, listen_port, send_port, user_hash = config

    try:
        async with anyio.create_task_group() as tg:
            tg.start_soon(read_messages, host, listen_port, messages_queue, save_queue, updates_queue)
            tg.start_soon(send_messages, host, send_port, user_hash, sending_queue, updates_queue)
            tg.start_soon(watch_for_sending, host, send_port, user_hash, updates_queue)

    except ConnectionError:
        logger.error("Trying to reconnect")


async def main():
    logging.basicConfig(
        format="[%(asctime)s.%(msecs).03d] %(levelname)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )

    filepath, config = parse_config()
    history = read_history(filepath)
    messages_queue = Queue()
    sending_queue = Queue()
    updates_queue = Queue()
    save_queue = Queue()

    try:
        async with anyio.create_task_group() as tg:
            tg.start_soon(draw, history, messages_queue, sending_queue, updates_queue)
            tg.start_soon(save_messages, filepath, save_queue)
            tg.start_soon(handle_connection, config, messages_queue, sending_queue, updates_queue, save_queue)

    except InvalidToken:
        messagebox.showwarning("Неверный токен", "Проверьте токен, сервер его не узнал")
        logger.error("Invalid account_hash")
        return

    except TkAppClosed:
        logging.debug("Client has been closed")


if __name__ == "__main__":
    anyio.run(main)

import asyncio
from argparse import ArgumentParser
from os import environ
from asyncio import Queue

import aiofiles

from gui import draw
from utils import open_connection, decode, format_log


# TODO: README
# TODO: Писать в логи статусы


def parse_config():
    parser = ArgumentParser()
    parser.add_argument("--host", type=str, help="Server host")
    parser.add_argument("--listen", type=int, help="Server listen port")
    parser.add_argument("--path", type=str, help="Relative path to logs file")
    args = parser.parse_args()

    host = args.host or environ.get("SERVER_HOST", "minechat.dvmn.org")
    port = args.listen or environ.get("SERVER_LISTEN_PORT", 5000)
    path = args.path or environ.get("LOG_PATH", ".")
    path.strip("/")

    return host, port, path


async def read_messages(host: str, port: int, messages_queue: Queue, save_queue: Queue):
    async with open_connection(host, port) as (reader, writer):
        while True:
            message = decode(await reader.readline())
            messages_queue.put_nowait(message)
            save_queue.put_nowait(message)
            # TODO: Проверить, что исходящие сообщения тоже записываются


async def save_messages(filepath: str, save_queue: Queue):
    async with aiofiles.open(f"{filepath}/logs.txt", "a") as logs:
        while True:
            message = await save_queue.get()
            await logs.write(format_log(message))


def read_history(filepath: str):
    with open(f"{filepath}/logs.txt", "r") as logs:
        messages = [line.rstrip("\n") for line in logs.readlines()]
        return messages


async def main():
    host, port, filepath = parse_config()

    messages_queue = Queue()
    sending_queue = Queue()
    status_updates_queue = Queue()
    save_queue = Queue()
    history = read_history(filepath)

    await asyncio.gather(
        draw(history, messages_queue, sending_queue, status_updates_queue),
        read_messages(host, port, messages_queue, save_queue),
        save_messages(filepath, save_queue),
    )


asyncio.run(main())

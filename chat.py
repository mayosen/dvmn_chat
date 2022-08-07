import asyncio
from argparse import ArgumentParser
from os import environ
from time import time

from gui import draw
from utils import open_connection, decode


# TODO: README


def parse_config():
    parser = ArgumentParser()
    parser.add_argument("--host", type=str, help="Server host")
    parser.add_argument("--listen", type=int, help="Server listen port")
    args = parser.parse_args()

    host = args.host or environ.get("SERVER_HOST", "minechat.dvmn.org")
    port = args.listen or environ.get("SERVER_LISTEN_PORT", 5000)

    return host, port


async def read_messages(host: str, port: int, messages_queue: asyncio.Queue):
    async with open_connection(host, port) as (reader, writer):
        while True:
            message = decode(await reader.readline())
            messages_queue.put_nowait(message)


async def main():
    host, port = parse_config()

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()

    await asyncio.gather(
        read_messages(host, port, messages_queue),
        draw(messages_queue, sending_queue, status_updates_queue),
    )


asyncio.run(main())

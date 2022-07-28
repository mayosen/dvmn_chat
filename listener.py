import asyncio
from argparse import ArgumentParser
from os import environ

import aiofiles

from utils import decode, format_log, open_connection


def parse_config():
    parser = ArgumentParser()
    parser.add_argument("--host", type=str, help="Server host")
    parser.add_argument("--port", type=int, help="Server port")
    parser.add_argument("--history", type=str, help="Relative path to logs")
    args = parser.parse_args()

    host = args.host or environ.get("SERVER_HOST", "minechat.dvmn.org")
    port = args.port or environ.get("SERVER_PORT", 5000)
    history = args.history or environ.get("HISTORY_PATH", ".")
    history = history.strip("/")

    return host, port, history


async def listen_socket(host: str, port: int, path: str):
    async with open_connection(host, port) as (reader, writer):
        async with aiofiles.open(f"{path}/logs.txt", "a") as log_file:
            log = format_log("--- Установлено соединение ---")
            print(log, end="")
            await log_file.write(f"{log}")

            while True:
                message = decode(await reader.readline())
                log = format_log(message)
                print(log, end="")
                await log_file.write(log)


if __name__ == "__main__":
    host, port, history = parse_config()
    asyncio.run(listen_socket(host, port, history))

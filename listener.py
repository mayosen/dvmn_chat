import asyncio
from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from os import environ

import aiofiles

from utils import decode


@dataclass
class Config:
    host: str
    port: int
    history: str

    @staticmethod
    def parse():
        parser = ArgumentParser()
        parser.add_argument("--host", type=str, help="Server host")
        parser.add_argument("--port", type=int, help="Server port")
        parser.add_argument("--history", type=str, help="Path to logs")
        args = parser.parse_args()

        host = args.host or environ.get("SERVER_HOST") or "minechat.dvmn.org"
        port = args.port or environ.get("SERVER_PORT") or 5000
        history = args.history or environ.get("HISTORY_PATH") or "."

        port = int(port)
        history = history.strip("/")

        return Config(host, port, history)


def format_log(message: str) -> str:
    return f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n"


async def tcp_client(host: str, port: int, path: str):
    reader, _ = await asyncio.open_connection(host, port)

    async with aiofiles.open(f"{path}/logs.txt", "a") as log_file:
        log = format_log("--- Установлено соединение ---")
        print(log, end="")
        await log_file.write(f"{log}")

        while True:
            response = await reader.readline()
            message = decode(response)
            log = format_log(message)
            print(log, end="")
            await log_file.write(log)


if __name__ == "__main__":
    config = Config.parse()
    asyncio.run(tcp_client(config.host, config.port, config.history))

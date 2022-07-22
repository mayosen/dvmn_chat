import asyncio
from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from os import environ

import aiofiles


def format_log(message: str):
    return f"[{datetime.now().strftime('%H:%M:%S')}] {message}"


async def tcp_client(host: str, port: int, path: str):
    reader, _ = await asyncio.open_connection(host, port)

    async with aiofiles.open(f"{path}/logs.txt", "a") as log_file:
        log = format_log("--- Установлено соединение ---\n")
        await log_file.write(log)

        while True:
            incoming_bytes = await reader.readline()
            message = incoming_bytes.decode("utf-8")
            log = format_log(message)
            print(log, end="")
            await log_file.write(log)


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

        host = args.host or environ.get("SERVER_HOST")
        port = args.port or environ.get("SERVER_PORT")
        history = args.history or environ.get("HISTORY_PATH")
        assert all([host, port, history]), "Need to configure project"

        port = int(port)
        history = history.strip("/")

        return Config(host, port, history)


if __name__ == "__main__":
    config = Config.parse()
    asyncio.run(tcp_client(config.host, config.port, config.history))

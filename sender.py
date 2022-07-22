import asyncio
import json
import logging
from argparse import ArgumentParser
from asyncio import StreamReader, StreamWriter
from dataclasses import dataclass
from os import environ

import aiofiles

from utils import decode, encode


@dataclass
class Config:
    host: str
    port: int
    credentials: str

    @staticmethod
    def parse():
        parser = ArgumentParser()
        parser.add_argument("--host", type=str, help="Server host")
        parser.add_argument("--port", type=int, help="Server port")
        parser.add_argument("--credentials", type=str, help="Path to credentials")
        args = parser.parse_args()

        host = args.host or environ.get("SERVER_HOST")
        port = args.port or environ.get("SERVER_PORT")
        credentials = args.credentials or environ.get("CREDENTIALS_PATH")
        assert all([host, port, credentials]), "Need to configure project"

        port = int(port)
        credentials = credentials.strip("/")

        return Config(host, port, credentials)


async def register(reader: StreamReader, writer: StreamWriter, path: str):
    writer.write(encode(""))
    logging.debug(f"Reader: {decode(await reader.readline())}")

    nickname = input()
    writer.write(encode(nickname))
    credentials = decode(await reader.readline())
    logging.debug(f"Reader: {credentials}")

    async with aiofiles.open(f"{path}/credentials.json", "w") as file:
        await file.write(credentials)


async def authorize(reader: StreamReader, writer: StreamWriter, user_hash: str) -> bool:
    writer.write(encode(user_hash))
    response = decode(await reader.readline())
    logging.debug(f"Reader: {response}")

    if not json.loads(response):
        logging.debug("Неизвестный токен. Проверьте его или зарегистрируйте заново.")
        return False

    return True


def submit_message(writer: StreamWriter):
    message = input()
    writer.write(encode(message + "\n"))


async def client(host: str, port: int, path: str):
    reader, writer = await asyncio.open_connection(host, port)
    response = await reader.readline()
    logging.debug(f"Reader: {decode(response)}")
    user_message = input()

    if not user_message:
        await register(reader, writer, path)
    else:
        if not await authorize(reader, writer, user_message):
            return

    logging.debug(f"Reader: {decode(await reader.readline())}")
    submit_message(writer)
    logging.debug(f"Reader: {decode(await reader.readline())}")

    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    logging.basicConfig(
        format=u"%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        level=logging.DEBUG,
        datefmt="%H:%M:%S",
    )
    config = Config.parse()

    asyncio.run(client(config.host, config.port, config.credentials))

import asyncio
import json
import logging
from argparse import ArgumentParser
from dataclasses import dataclass
from os import environ


def decode(message: bytes) -> str:
    return message.decode("utf-8").rstrip("\n")


def encode(message: str) -> bytes:
    return bytes(message, "utf-8")


async def sender(host: str, port: int, account_hash: str):
    reader, writer = await asyncio.open_connection(host, port)
    logging.debug(f"Reader: {decode(await reader.readline())}")

    writer.write(encode(f"{account_hash}\n"))
    response = decode(await reader.readline())
    message = json.loads(response)

    if not message:
        logging.debug("Неизвестный токен. Проверьте его или зарегистрируйте заново.")
        return
    else:
        logging.debug(f"Reader: {message}")

    writer.write(encode("Третье сообщение\n\n"))
    logging.debug(f"Reader: {decode(await reader.readline())}")

    writer.close()
    await writer.wait_closed()


@dataclass
class Config:
    host: str
    port: int
    user_hash: str

    @staticmethod
    def parse():
        parser = ArgumentParser()
        parser.add_argument("--host", type=str, help="Server host")
        parser.add_argument("--port", type=int, help="Server port")
        parser.add_argument("--hash", type=int, help="User hash to access server")
        args = parser.parse_args()

        host = args.host or environ.get("SERVER_HOST")
        port = args.port or environ.get("SERVER_PORT")
        account_hash = args.hash or environ.get("USER_HASH")
        assert all([host, port, account_hash]), "Need to configure project"

        port = int(port)

        return Config(host, port, account_hash)


if __name__ == "__main__":
    logging.basicConfig(
        format=u"%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        level=logging.DEBUG,
        datefmt="%H:%M:%S",
    )
    config = Config.parse()

    asyncio.run(sender(config.host, config.port, config.user_hash))

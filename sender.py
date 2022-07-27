import asyncio
import json
from argparse import ArgumentParser
from asyncio import StreamReader, StreamWriter
from os import environ

from utils import decode, encode, open_connection


def parse_config():
    parser = ArgumentParser(description="Pass exactly one option: --hash or --nickname.")
    parser.add_argument("--host", type=str, help="Server host")
    parser.add_argument("--port", type=int, help="Server port")
    parser.add_argument("--hash", type=str, help="Account hash to access host")
    parser.add_argument("--nickname", type=str, help="Preferred nickname to register")
    parser.add_argument("--message", type=str, help="Message to send")
    args = parser.parse_args()

    host = args.host or environ.get("SERVER_HOST", "minechat.dvmn.org")
    port = args.port or environ.get("SERVER_PORT", 5050)
    user_hash = args.hash or environ.get("USER_HASH")
    nickname = args.nickname or environ.get("NICKNAME")
    message = args.message or environ.get("MESSAGE")

    assert bool(user_hash) != bool(nickname), "Pass exactly one option: --hash or --nickname"
    assert message, "Pass message option"

    return host, port, user_hash, nickname, message


async def register(host: str, port: int, nickname: str) -> str:
    async with open_connection(host, port) as (reader, writer):
        await reader.readline()  # Hello username
        writer.write(encode(""))
        await writer.drain()

        await reader.readline()  # Enter preferred nickname
        nickname = nickname.replace("\n", "")
        writer.write(encode(nickname))
        await writer.drain()

        response = decode(await reader.readline())
        return json.loads(response)["account_hash"]


class InvalidHash(Exception):
    """Invalid account_hash."""


async def authorize(reader: StreamReader, writer: StreamWriter, user_hash: str):
    await reader.readline()  # Enter hash
    writer.write(encode(user_hash))
    await writer.drain()

    response = decode(await reader.readline())  # Credentials
    user_info = json.loads(response)

    if not user_info:
        raise InvalidHash


async def submit_message(reader: StreamReader, writer: StreamWriter, message: str):
    await reader.readline()  # Welcome to chat
    message = message.replace("\n", "")
    writer.write(encode(message + "\n"))
    await writer.drain()
    await reader.readline()  # Write more


async def send_message(host: str, port: int, user_hash: str, nickname: str, message: str):
    if nickname:
        user_hash = await register(host, port, nickname)

    async with open_connection(host, port) as (reader, writer):
        try:
            await authorize(reader, writer, user_hash)
            await submit_message(reader, writer, message)
        except InvalidHash:
            print("Неизвестный токен. Проверьте его или зарегистрируйте заново.")


if __name__ == "__main__":
    config_args = parse_config()
    asyncio.run(send_message(*config_args))

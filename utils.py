import asyncio
from contextlib import asynccontextmanager
from datetime import datetime


ENCODING = "utf-8"


def format_log(message: str) -> str:
    return f"[{datetime.now().strftime('%d.%m %H:%M:%S')}] {message}\n"


def decode(message: bytes) -> str:
    return message.decode(ENCODING).rstrip("\n")


def encode(message: str) -> bytes:
    return bytes(f"{message}\n", ENCODING)


@asynccontextmanager
async def open_connection(host: str, port: int):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()

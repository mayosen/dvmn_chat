import asyncio
from contextlib import asynccontextmanager
from datetime import datetime


def format_log(message: str) -> str:
    return f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n"


def decode(message: bytes) -> str:
    return message.decode("utf-8").rstrip("\n")


def encode(message: str) -> bytes:
    return bytes(f"{message}\n", "utf-8")


@asynccontextmanager
async def safe_connection(host: str, port: int):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()

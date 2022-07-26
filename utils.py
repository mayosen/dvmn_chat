import asyncio
from asyncio import StreamReader, StreamWriter
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncContextManager


def format_log(message: str) -> str:
    return f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n"


def decode(message: bytes) -> str:
    return message.decode("utf-8").rstrip("\n")


def encode(message: str) -> bytes:
    return bytes(f"{message}\n", "utf-8")


@asynccontextmanager
async def safe_connection(host: str, port: int) -> AsyncContextManager[tuple[StreamReader, StreamWriter]]:
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()

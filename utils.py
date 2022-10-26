import asyncio
import socket
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime

ENCODING = "utf-8"


def decode(message: bytes) -> str:
    return message.decode(ENCODING).rstrip("\n")


def encode(message: str) -> bytes:
    return bytes(f"{message}\n", ENCODING)


def format_log(message: str) -> str:
    return f"[{datetime.now().strftime('%d.%m %H:%M:%S')}] {message}\n"


@asynccontextmanager
async def open_connection(host: str, port: int):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()


class Socket(socket.socket):
    _buffer_size = 1024

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def receive(self):
        data = bytearray()
        while True:
            temp = self.recv(Socket._buffer_size)
            if temp == b"\n":
                continue
            if temp:
                data.extend(temp)
            if not temp or len(temp) < Socket._buffer_size:
                break

        return bytes(data)


@contextmanager
def open_socket(host: str, port: int):
    sock = Socket()
    try:
        sock.connect((host, port))
        yield sock
    finally:
        sock.close()

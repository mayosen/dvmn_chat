import asyncio
from datetime import datetime

import aiofiles


def format_log(message: str):
    return f"[{datetime.now().strftime('%H:%M:%S')}] {message}"


async def tcp_client():
    reader, writer = await asyncio.open_connection("minechat.dvmn.org", 5000)

    async with aiofiles.open("logs.txt", "a") as log_file:
        log = format_log("Установлено соединение\n")
        await log_file.write(log)

        while True:
            incoming_bytes = await reader.readline()
            message = incoming_bytes.decode("utf-8")
            log = format_log(message)
            print(log, end="")
            await log_file.write(log)
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(tcp_client())

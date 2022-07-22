import asyncio


async def tcp_client():
    reader, writer = await asyncio.open_connection("minechat.dvmn.org", 5000)

    while True:
        message = await reader.readline()
        print(message.decode("utf-8"), end="")
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(tcp_client())

import asyncio

from gui import draw


messages_queue = asyncio.Queue()
sending_queue = asyncio.Queue()
status_updates_queue = asyncio.Queue()

asyncio.run(draw(messages_queue, sending_queue, status_updates_queue))

from asyncio.runners import run
from asyncio.futures import Future
from websockets import serve
from websockets.legacy.protocol import broadcast
from module.logger import logger

client = set()

async def echo(websocket):
    client.add(websocket)
    try:
        async for message in websocket:
            logger.info(message)
            broadcast(client, message)
    finally:
        client.remove(websocket)

async def main():
    async with serve(echo, "localhost", 3000):
        await Future()

run(main())


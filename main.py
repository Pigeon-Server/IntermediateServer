from asyncio.runners import run
from asyncio.futures import Future
from websockets import serve
from websockets.legacy.protocol import broadcast
from module.logger import logger

clientData = {}
client = set()

async def SendMessage(websocket, data: str, connection: str = "keep-alive", uuid: str = None) -> None:
    await websocket.send(str({
            "type": "Server",
            "connection": connection,
            "from": uuid,
            "to": str(websocket.id),
            "load": data
        }))

async def echo(websocket):  # 连接处理函数
    logger.info(f"Connection from {websocket.remote_address[0]}:{websocket.remote_address[1]}, UUID: {websocket.id}")
    try:
        message = eval(await websocket.recv())  # 编码收到的数据
        keys = message.keys()
        if "load" not in keys or "type" not in keys or "client" not in keys or "name" not in keys:  # 判断是否包含信息
            await websocket.close(1000, "Missing parameter")
        if message["load"] == "ClientHello" and message["type"] == "Client":
            client.add(websocket)
            uuid = str(websocket.id)  # 获取uuid
            logger.debug("Received client handshake packet.")
            logger.info(f"ClientInfo - name:{message['name']}, uuid:{uuid}")
            clientData[uuid] = {
                'name': message['name'],
                'client': message['client'],
                'socket': websocket
            }  # 记录客户端对应信息
            logger.debug("Sending server handshake packet.")
            await websocket.send(str({
                "type": "Server",
                "load": "ServerHello",
                "connection": "keep-alive",
                "uuid": uuid
            }))
            logger.success("Success. Link established. Waiting for message.")
            async for message in websocket:
                logger.info(f"Receive message package from {uuid}")
                message = eval(message)
                keys = message.keys()
                if "uuid" not in keys or message["uuid"] != uuid:
                    client.discard(websocket)
                    await websocket.close(1000, "Invalid uuid")
                elif "type" not in keys:
                    client.discard(websocket)
                    await websocket.close(1000, "Invalid type")
                if "connection" in keys:
                    if message["connection"] == "close":
                        client.discard(websocket)
                        await websocket.close(1000, "Connection close")
                    elif message["connection"] == "keep-alive":
                        logger.info(f"[{websocket.id}]: {message['load']}")
                        load = message["load"]
                        if message["broadcast"]:
                            client.discard(websocket)
                            broadcast(client, str(message))
                            client.add(websocket)
                        if 'target' in message.keys() and message['target'] != "":
                            await clientData[message['target']]['socket'].send(message['load'])
                        await websocket.send("Success")
        else:
            await websocket.close(1000, "The first packet is not ClientHello.")
    except Exception as error:
        logger.error(error)
    finally:
        if str(websocket.id) in clientData.keys():
            del clientData[str(websocket.id)]
        client.discard(websocket)

async def main():
    async with serve(echo, "0.0.0.0", 3000):
        logger.info("Server is running on port 3000")
        await Future()

run(main())


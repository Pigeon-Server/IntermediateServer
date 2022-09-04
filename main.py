from asyncio.runners import run
from asyncio.futures import Future
from websockets import serve
from websockets.legacy.protocol import broadcast
from module.logger import logger
from module.config import config

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


async def eventHandler(websocket):  # 连接处理函数
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
            date = {}
            for raw in clientData:
                if raw != uuid:
                    date[raw] = clientData[raw]['name']
            await websocket.send(str({
                "type": "Server",
                "load": "ServerHello",
                "connection": "keep-alive",
                "uuid": uuid,
                "clientInfo": str(date)
            }))
            client.discard(websocket)
            broadcast(client, str({
                "type": "OnlineBroadcast",
                "uuid": uuid,
                "name": message["name"]
            }))
            client.add(websocket)
            logger.success("Success. Link established. Waiting for message.")
            async for message in websocket:
                logger.info(f"Receive message package from {uuid}")
                message = eval(message)
                keys = message.keys()
                if "uuid" not in keys or message["uuid"] != uuid:
                    await websocket.close(1000, "Invalid uuid")
                elif "type" not in keys:
                    await websocket.close(1000, "Invalid type")
                if "connection" in keys and message["connection"] == "keep-alive":
                    if "load" in keys:
                        load = message["load"]
                        logger.info(f"[{clientData[uuid]['name']({uuid})}] : {str(load)}")
                        if "broadcast" in keys and message["broadcast"]:
                            client.discard(websocket)
                            broadcast(client, str({
                                "type": "Server",
                                "connection": "keep-alive",
                                "from": uuid,
                                "load": str(load)
                            }))
                            client.add(websocket)
                        elif 'target' in keys and message['target'] != "":
                            target = message['target']
                            if isinstance(target, str) and target in clientData.keys():
                                await SendMessage(clientData[target]['socket'], str(load), uuid=uuid)
                            elif isinstance(target, list):
                                for raw in target:
                                    if raw in clientData.keys():
                                        await SendMessage(clientData[raw]['socket'], str(load), uuid=uuid)
                    else:
                        await websocket.close(1000, "Invalid type")
                    await websocket.send("Success")
                else:
                    await websocket.close(1000, "Connection close")
        else:
            await websocket.close(1000, "The first packet is not ClientHello.")
    except Exception as error:
        logger.error(error)
        await websocket.close(1001, "Server Error")
    finally:
        client.discard(websocket)
        broadcast(client, str({
            "type": "OfflineBroadcast",
            "uuid": str(websocket.id)
        }))
        if str(websocket.id) in clientData.keys():
            del clientData[str(websocket.id)]

async def main():
    async with serve(eventHandler, config["Host"], config["Port"]):
        logger.info(f"Server is running at ws://{config['Host']}:{config['Port']}")
        logger.info("\n  _____  _                               _____                               \n"
                    " |  __ \\(_)                             / ____|                              \n"
                    " | |__) |_   __ _   ___   ___   _ __   | (___    ___  _ __ __   __ ___  _ __ \n"
                    " |  ___/| | / _` | / _ \\ / _ \\ | '_ \\   \\___ \\  / _ \\| '__|\\ \\ / // _ \\| '__|\n"
                    " | |    | || (_| ||  __/| (_) || | | |  ____) ||  __/| |    \\ V /|  __/| |   \n"
                    " |_|    |_| \\__, | \\___| \\___/ |_| |_| |_____/  \\___||_|     \\_/  \\___||_|   \n"
                    "             __/ |                                                           \n"
                    "            |___/                                                            "
                    "\n\n[Github源码库地址，欢迎贡献&完善&Debug]\nhttps://github.com/Pigeon-Server/IntermediateServer.git")
        await Future()


run(main())

import asyncio
from datetime import datetime
from os import environ

from swordi.client.log import Logger
from swordi.messages import *


SERVER_IP = environ.get("SWORDI_HOST", "127.0.0.1")
SERVER_PORT = environ.get("SWORDI_PORT", 9999)

PINGS = {}

logger = Logger()


async def await_seconds(seconds, method):
    await asyncio.sleep(seconds)
    method()


class ClientProtocol(asyncio.Protocol):
    def __init__(self, on_con_lost, loop):
        self.loop = loop
        self.on_con_lost = on_con_lost

    async def send_messages(self):
        while True:
            msg = await msgqueue.get()
            self.transport.write(msg.serialize())

    def connection_made(self, transport):
        logger.log("Connected to server!")
        self.transport = transport
        message = AuthMessage(token="caca")
        self.transport.write(message.serialize())
        self.send_ping()
        self.loop.create_task(self.send_messages())

    def data_received(self, data):
        messages = get_messages(data)
        for message in messages:
            if isinstance(message, PongMessage):
                if message.data["uuid"] in PINGS:
                    now = datetime.now()
                    diff = now - PINGS[message.data["uuid"]]
                    logger.latency.text = f"{diff.microseconds/1e+6}ms"

                    asyncio.get_running_loop().create_task(
                        await_seconds(10, self.send_ping)
                    )

            if isinstance(message, SimpleLogMessage):
                logger.log(message.data["message"])

            if isinstance(message, RoomSayMessage):
                logger.log(f"[{message.data['peer_id']}]: {message.data['message']}")

    def send_ping(self):
        message = PingMessage()
        PINGS[message.data["uuid"]] = datetime.now()
        self.transport.write(message.serialize())

    def connection_lost(self, exc):
        logger.log("Connection lost!")
        self.on_con_lost.set_result(True)


async def start_connection():
    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()
    reconnect_seconds = 5

    logger.log("Connecting to server...\n")

    while True:
        try:
            transport, protocol = await loop.create_connection(
                lambda: ClientProtocol(on_con_lost, loop), SERVER_IP, SERVER_PORT
            )

            try:
                await on_con_lost
            finally:
                transport.close()
        except OSError:
            # COnnection error
            logger.log(
                f"Can't connect to server, retrying in {reconnect_seconds} seconds"
            )
            await asyncio.sleep(reconnect_seconds)
        else:
            break

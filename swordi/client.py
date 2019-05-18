import asyncio
import random
import time
from datetime import datetime

from swordi.messages import PingMessage, PongMessage, AuthMessage, get_messages


SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999

PINGS = {}


class ClientProtocol(asyncio.Protocol):
    def __init__(self, on_con_lost, loop):
        self.loop = loop
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        self.transport = transport
        message = AuthMessage(token="caca")
        self.transport.write(message.serialize())
        self.send_ping()

    def data_received(self, data):
        messages = get_messages(data)
        for message in messages:
            print(f"[IN] {message}")
            if isinstance(message, PongMessage):
                if message.data["uuid"] in PINGS:
                    now = datetime.now()
                    diff = now - PINGS[message.data["uuid"]]
                    print(f"[Latency] {diff.microseconds}μs")
            time.sleep(random.randint(1, 3))
            self.send_ping()

    def send_ping(self):
        message = PingMessage()
        PINGS[message.data["uuid"]] = datetime.now()
        self.transport.write(message.serialize())
        print(f"[OUT] {message}")

    def connection_lost(self, exc):
        print("The server closed the connection")
        self.on_con_lost.set_result(True)


async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()

    transport, protocol = await loop.create_connection(
        lambda: ClientProtocol(on_con_lost, loop),
        SERVER_IP, SERVER_PORT
    )

    # Wait until the protocol signals that the connection
    # is lost and close the transport.
    try:
        await on_con_lost
    finally:
        transport.close()


def start():
    asyncio.run(main())

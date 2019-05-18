import asyncio

from swordi.messages import get_messages, PongMessage, PingMessage, AuthMessage


INTERFACE = "127.0.0.1"
PORT = 9999


class AuthService:
    @classmethod
    def authorize(cls, token):
        return token == "caca"


class ServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        self.authorized = False
        print(f'[NEW] {self.peername}')
        self.transport = transport

    def data_received(self, data):
        messages = get_messages(data)

        for message in messages:
            print(f'[IN] {self.peername}: {message}')

            if isinstance(message, PingMessage):
                if self.authorized:
                    response = PongMessage(uuid=message.data["uuid"])
                    print(f"[OUT] {response}")
                    self.transport.write(response.serialize())

            if isinstance(message, AuthMessage):
                if AuthService.authorize(message.data["token"]):
                    print(f'[AUTH] Logged in {self.peername}')
                    self.authorized = True
                else:
                    print(f'[AUTH] Failed for {self.peername}')
                    self.transport.close()

    def connection_lost(self, exc):
        print(f"[LOST] {self.peername}")


async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: ServerProtocol(), INTERFACE, PORT)

    async with server:
        await server.serve_forever()


def start():
    print(f"Starting server on {INTERFACE}:{PORT}")
    asyncio.run(main())

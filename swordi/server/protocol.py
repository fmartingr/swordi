import asyncio
from os import environ

from swordi.messages import (
    get_messages,
    RoomJoinMessage,
    RoomLeaveMessage,
    RoomSayMessage,
    PongMessage,
    PingMessage,
    AuthMessage,
    SimpleLogMessage,
)


SWORDI_HOST = environ.get("SWORDI_HOST", "127.0.0.1")
SWORDI_PORT = environ.get("SWORDI_PORT", 9999)


ROOMS = {}
PEERS = {}


class AuthService:
    @classmethod
    def authorize(cls, token):
        return token == "caca"


class RoomService:
    @classmethod
    def _send_message_to_peer(cls, peer_id, message):
        msg = SimpleLogMessage(message=message)
        PEERS[peer_id].transport.write(msg.serialize())

    @classmethod
    def _send_message_to_room(cls, room_name, message, exclude=None):
        exclude = exclude or []
        for peer in ROOMS[room_name]:
            if peer not in exclude:
                cls._send_message_to_peer(peer, message)

    @classmethod
    def join(cls, peer_id, room_name):
        cls.leave(peer_id)

        if room_name not in ROOMS:
            ROOMS[room_name] = set()
        ROOMS[room_name].add(peer_id)
        cls._send_message_to_peer(peer_id, f"Joined {room_name}")
        cls._send_message_to_room(room_name, f'[{peer_id}] joined!', exclude=[peer_id])

    @classmethod
    def leave(cls, peer_id):
        room_name = cls._get_current_peer_room(peer_id)
        if not room_name:
            return

        ROOMS[room_name].remove(peer_id)
        cls._send_message_to_peer(peer_id, f"Left {room_name}")
        cls._send_message_to_room(room_name, f'[{peer_id}] left!', exclude=[peer_id])

        if not len(ROOMS[room_name]):
            del ROOMS[room_name]

    @classmethod
    def _get_current_peer_room(cls, peer_id):
        for room_name, peers in ROOMS.items():
            if peer_id in peers:
                return room_name

    @classmethod
    def say(cls, peer_id, message):
        room_name = cls._get_current_peer_room(peer_id)
        if not room_name:
            cls._send_message_to_peer(peer_id, 'You are not in a room!')
            return

        msg = RoomSayMessage(room_name=room_name, peer_id=peer_id, message=message)
        for peer in ROOMS[room_name]:
            PEERS[peer].transport.write(msg.serialize())


class ServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.peername = transport.get_extra_info("peername")
        self.authorized = False
        print(f"[NEW] {self.peername}")
        self.transport = transport

    def data_received(self, data):
        messages = get_messages(data)

        for message in messages:
            print(f"[IN] {self.peername}: {message}")

            if isinstance(message, PingMessage):
                if self.authorized:
                    response = PongMessage(uuid=message.data["uuid"])
                    print(f"[OUT] {response}")
                    self.transport.write(response.serialize())

            if isinstance(message, AuthMessage):
                if AuthService.authorize(message.data["token"]):
                    print(f'[AUTH] Logged in: {message.data["peer_id"]}')
                    self.authorized = True
                    self.peername = message.data["peer_id"]
                    PEERS[self.peername] = self
                else:
                    print(f"[AUTH] Failed for {self.peername}")
                    self.transport.close()

            if isinstance(message, RoomJoinMessage):
                RoomService.join(self.peername, message.data["room_name"])

            if isinstance(message, RoomSayMessage):
                RoomService.say(self.peername, message.data["message"])

            if isinstance(message, RoomLeaveMessage):
                RoomService.leave(self.peername)

    def connection_lost(self, exc):
        print(f"[LOST] {self.peername}")
        RoomService.leave(self.peername)
        del PEERS[self.peername]


async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: ServerProtocol(), SWORDI_HOST, SWORDI_PORT
    )

    async with server:
        await server.serve_forever()

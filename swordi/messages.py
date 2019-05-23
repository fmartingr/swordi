import asyncio
import copy
import uuid

import msgpack


msgqueue = asyncio.Queue()


class Message:
    default_data = {}

    def __init__(self, *args, **kwargs):
        self.data = copy.copy(self.default_data)
        self.data.update(kwargs)

    def __repr__(self):
        params = " ".join([f"{key}={value}" for key, value in self.data.items()])
        _repr = " ".join([self.__class__.__name__, params])
        return f"<{_repr}>"

    @property
    def repr(self):
        data = {"type": self.__class__.__name__}
        data.update(self.data)
        return data

    def serialize(self):
        return msgpack.packb(self.repr)

    def queue(self):
        asyncio.get_running_loop().create_task(msgqueue.put(self))


class PingMessage(Message):
    data = {}

    def __init__(self, *args, **kwargs):
        # Init with an UUID but override it if came from param
        super().__init__(*args, **kwargs)
        if "uuid" not in self.data:
            self.data["uuid"] = str(uuid.uuid4())


class PongMessage(Message):
    pass


class SimpleLogMessage(Message):
    default_data = {"message": None}


class AuthMessage(Message):
    default_data = {"token": None, "peer_id": None}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.data["peer_id"]:
            self.data["peer_id"] = str(uuid.uuid4())[0:13]


class RoomJoinMessage(Message):  # Used to change room
    default_data = {"room_name": None}


class RoomLeaveMessage(Message):
    pass


class RoomSayMessage(Message):
    default_data = {"message": None, "room_name": None, "peer_id": None}


def get_messages(data):
    from io import BytesIO

    unpacked = msgpack.Unpacker(BytesIO(data), raw=False)
    for msg in unpacked:
        message_type = msg.pop("type")
        yield MESSAGES[message_type](**msg)


MESSAGES = (
    PingMessage,
    PongMessage,
    AuthMessage,
    RoomJoinMessage,
    RoomLeaveMessage,
    RoomSayMessage,
    SimpleLogMessage,
)
MESSAGES = {cls.__name__: cls for cls in MESSAGES}

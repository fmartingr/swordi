import copy
import uuid

import msgpack


class Message:
    default_data = {}

    def __init__(self, *args, **kwargs):
        self.data = copy.copy(self.default_data)
        self.data.update(kwargs)

    def __repr__(self):
        params = ' '.join([
            f"{key}={value}" for key, value in self.data.items()])
        _repr = ' '.join([self.__class__.__name__, params])
        return f"<{_repr}>"

    @property
    def repr(self):
        data = {
            "type": self.__class__.__name__,
        }
        data.update(self.data)
        return data

    def serialize(self):
        return msgpack.packb(self.repr)


class PingMessage(Message):
    data = {}

    def __init__(self, *args, **kwargs):
        # Init with an UUID but override it if came from param
        super().__init__(*args, **kwargs)
        if "uuid" not in self.data:
            self.data["uuid"] = str(uuid.uuid4())


class PongMessage(Message):
    pass


class AuthMessage(Message):
    default_data = {
        "token": None
    }


def get_messages(data):
    from io import BytesIO
    unpacked = msgpack.Unpacker(BytesIO(data), raw=False)
    for msg in unpacked:
        message_type = msg.pop("type")
        yield MESSAGES[message_type](**msg)


MESSAGES = (PingMessage, PongMessage, AuthMessage, )
MESSAGES = {cls.__name__: cls for cls in MESSAGES}

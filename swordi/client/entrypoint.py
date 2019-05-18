import asyncio

from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.patch_stdout import patch_stdout

from swordi.client.ui import clientui
from swordi.client.protocol import start_connection


def start():
    loop = asyncio.get_event_loop()

    use_asyncio_event_loop(loop)

    loop.create_task(start_connection())

    with patch_stdout():
        loop.run_until_complete(clientui.run_async().to_asyncio_future())
    # loop.run_forever()

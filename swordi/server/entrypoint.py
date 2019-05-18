import asyncio

from swordi.server.protocol import main
from swordi.config import SWORDI_HOST, SWORDI_PORT


def start():
    print(f"Starting server on {SWORDI_HOST}:{SWORDI_PORT}")
    asyncio.run(main())

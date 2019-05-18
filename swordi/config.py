from os import environ


SWORDI_HOST = environ.get("SWORDI_HOST", "127.0.0.1")
SWORDI_PORT = environ.get("SWORDI_PORT", 9999)

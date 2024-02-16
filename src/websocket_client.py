import os
from websockets.sync.client import connect

SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")


def hello():
    with connect(f"ws://{SERVER_ADDRESS}") as websocket:
        websocket.send("Hello world!")
        message = websocket.recv()
        print(f"Received: {message}")


hello()

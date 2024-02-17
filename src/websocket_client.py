import os
from dotenv import load_dotenv
from websockets.sync.client import connect
from create_dotenv import create_dotenv


def hello(SERVER_ADDRESS):
    with connect(f"ws://{SERVER_ADDRESS}") as websocket:
        websocket.send("Hello world!")
        message = websocket.recv()
        print(f"Received: {message}")


while True:
    try:
        dotenv_fp = os.path.join("config", ".env")
        exists = os.path.isfile(dotenv_fp)
        if not exists:
            create_dotenv()

        load_dotenv(dotenv_path=dotenv_fp, override=True)
        SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")

        hello(SERVER_ADDRESS=SERVER_ADDRESS)

        break

    except Exception as e:
        print(f"Connection failed: {e}. Retry...")
        create_dotenv(remove=True)

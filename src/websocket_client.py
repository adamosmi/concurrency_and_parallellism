import os
from dotenv import load_dotenv
import websockets
from create_dotenv import create_dotenv
import asyncio


class AsyncClient:
    def __init__(self, server_address):
        self.name = input("Enter username (public):\n")
        self.server_address = server_address
        self.msgs_sent = []
        self.msgs_recieved = []

    # define async input function
    async def async_input(self, prompt):
        return await asyncio.to_thread(input, prompt)

    # send message and store in msgs_sent
    async def send_message(self, websocket):
        while True:
            message_text = await self.async_input(prompt="Message:\n")
            await websocket.send(f"{self.name}: {message_text}")
            self.msgs_sent.append(message_text)
            print(f"Message sent:\n{message_text}")

    async def recieve_messages(self, websocket):
        while True:
            try:
                message_text = await websocket.recv()
                self.msgs_recieved.append(message_text)
                print(f"Message recieved:\n{message_text}")
            except websockets.ConnectionClosed as e:
                print(f"Connection closed: {e.reason}")
                break

    async def client_handler(self):
        # connect to server
        async with websockets.connect(f"ws://{self.server_address}") as websocket:
            # send server a message
            tasks = [self.send_message(websocket), self.recieve_messages(websocket)]
            await asyncio.gather(*tasks)


# Main loop to attempt to connect to the server
while True:
    try:
        # Define the path to the .env file
        dotenv_fp = os.path.join("config", ".env")
        # Check if the .env file exists
        exists = os.path.isfile(dotenv_fp)
        # If the .env file does not exist, create it
        if not exists:
            create_dotenv()

        # Load environment variables from the .env file, overriding existing ones
        load_dotenv(dotenv_path=dotenv_fp, override=True)
        # Retrieve the server address from the environment variables
        SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
        client = AsyncClient(server_address=SERVER_ADDRESS)

        # Attempt to send a message to the server
        # hello(SERVER_ADDRESS=SERVER_ADDRESS)
        asyncio.run(client.client_handler())

        # If successful, break out of the loop
        break

    except Exception as e:
        # If the connection fails, print the error and retry
        print(f"Connection failed: {e}. Retry...")
        # Optionally, remove the existing .env file before retrying
        create_dotenv(remove=True)

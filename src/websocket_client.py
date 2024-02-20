import os
from dotenv import load_dotenv
import websockets
from create_dotenv import create_dotenv
import asyncio


# define async input function
async def async_input(prompt):
    return await asyncio.to_thread(input, prompt)


async def send_message(websocket):
    while True:
        message = await async_input(prompt="Message:\n")
        await websocket.send(message)
        print(f"Message sent:\n{message}")


async def recieve_messages(websocket):
    while True:
        try:
            message = await websocket.recv()
            print(f"Message recieved:\n{message}")
        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e.reason}")
            break


async def client_handler(SERVER_ADDRESS):
    # connect to server
    async with websockets.connect(f"ws://{SERVER_ADDRESS}") as websocket:
        # send server a message
        tasks = [send_message(websocket), recieve_messages(websocket)]
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

        # Attempt to send a message to the server
        # hello(SERVER_ADDRESS=SERVER_ADDRESS)
        asyncio.run(client_handler(SERVER_ADDRESS=SERVER_ADDRESS))

        # If successful, break out of the loop
        break

    except Exception as e:
        # If the connection fails, print the error and retry
        print(f"Connection failed: {e}. Retry...")
        # Optionally, remove the existing .env file before retrying
        create_dotenv(remove=True)

import os
from dotenv import load_dotenv
from websockets.sync.client import connect
from create_dotenv import create_dotenv


# def hello(SERVER_ADDRESS):
#     """
#     Establishes a websocket connection to the server, sends a "Hello world!" message,
#     and prints the response received from the server.
#
#     Args:
#     - SERVER_ADDRESS (str): The address of the server to connect to.
#     """
#     # Establish a connection to the websocket server
#     with websockets.sync.client.connect(f"ws://{SERVER_ADDRESS}") as websocket:
#         # Send a message to the server
#         websocket.send("Hello world!")
#         # Wait for and receive a response from the server
#         message = websocket.recv()
#         # Print the received message
#         print(f"Received: {message}")


def client_handler(SERVER_ADDRESS):
    # connect to server
    with connect(f"ws://{SERVER_ADDRESS}") as websocket:
        # send server a message
        while True:
            message = input("Message:\n")
            websocket.send(message)
            print("Message sent\n")


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
        client_handler(SERVER_ADDRESS=SERVER_ADDRESS)

        # If successful, break out of the loop
        break

    except Exception as e:
        # If the connection fails, print the error and retry
        print(f"Connection failed: {e}. Retry...")
        # Optionally, remove the existing .env file before retrying
        create_dotenv(remove=True)

# Example file showing a circle moving on screen
import pygame
import os
from dotenv import load_dotenv
import websockets
from create_dotenv import create_dotenv
import asyncio
import json


class AsyncClient:
    def __init__(self, server_address):
        self.name = input("Enter username (public):\n")
        self.clear_screen()
        self.server_address = server_address
        self.msgs_sent = []
        self.msgs_recieved = []

    # define async input function
    async def async_input(self, prompt):
        return await asyncio.to_thread(input, prompt)

    # send message and store in msgs_sent
    async def send_message(self, websocket):
        while True:
            message_text = await self.async_input(prompt=f"(you) {self.name}:\n")
            message = {"name": self.name, "message_text": message_text}
            await websocket.send(json.dumps(message))
            self.msgs_sent.append(message_text)

    # receive messages and store in msgs_received, excluding own messages sent
    async def recieve_messages(self, websocket):
        while True:
            try:
                # get message
                message_text = await websocket.recv()
                # load message string to dict
                message = json.loads(message_text)
                # store message
                self.msgs_recieved.append(message)
                # output message
                self.clear_screen()  # clear prior messages
                for msg in self.msgs_recieved[
                    -len(self.msgs_recieved) :
                ]:  # show only last n messages
                    print(msg.get("name") + ": " + msg.get("message_text"))
                print(f"(you) {self.name}:")
            except websockets.ConnectionClosed as e:
                print(f"Connection closed: {e.reason}")
                break

    # calls send and receive message functions
    async def client_handler(self):
        # connect to server
        async with websockets.connect(f"ws://{self.server_address}") as websocket:
            # send and receive messages from the server asynchronously
            tasks = [self.send_message(websocket), self.recieve_messages(websocket)]
            await asyncio.gather(*tasks)

    # clear screen of previous output
    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")


class Player:
    def __init__(self):
        self.pos = None
        self.id = None


class Game(AsyncClient):
    def __init__(self, server_address):
        super().__init__(server_address)
        self.players = {}
        # game vars
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.init_player_pos = pygame.Vector2(
            self.screen.get_width() / 2, self.screen.get_height() / 2
        )
        # for dev
        self.id = 1

    # calls send and receive message functions, and start the game
    async def client_handler(self):
        # connect to server
        async with websockets.connect(f"ws://{self.server_address}") as websocket:
            self.websocket = websocket
            # send and receive messages from the server asynchronously
            tasks = [
                # self.receive_position(self.websocket),
                self.start_game(),  # line added for Game class
            ]
            await asyncio.gather(*tasks)

    async def calc_position(self, pos, keys, dt):
        player_pos = pos.copy()  # make a copy to avoid unintentional updates
        if keys[pygame.K_w]:
            player_pos.y -= 300 * dt
        if keys[pygame.K_s]:
            player_pos.y += 300 * dt
        if keys[pygame.K_a]:
            player_pos.x -= 300 * dt
        if keys[pygame.K_d]:
            player_pos.x += 300 * dt
        return player_pos

    # send position, no loop because is only called after updating once per frame
    async def send_position(self, pos, websocket):
        # while True:
        player_pos_x = pos.x
        player_pos_y = pos.y
        message = {"id": self.id, "pos_x": player_pos_x, "pos_y": player_pos_y}
        await websocket.send(json.dumps(message))

    # receive position, continuously running proccess alongside the game
    async def receive_position(self, websocket):
        try:
            # get message
            message_text = await websocket.recv()
            # load message string to dict
            message = json.loads(message_text)
            player_id = message.get("id")
            player_pos_x = message.get("pos_x")
            player_pos_y = message.get("pos_y")

            print(f"x: {player_pos_x}, y: {player_pos_x}")
            return pygame.Vector2(player_pos_x, player_pos_y)

        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e.reason}")

    async def set_position(self, id, pos, keys, dt):
        player_pos = pos
        if keys[pygame.K_w]:
            player_pos.y -= 300 * dt
        if keys[pygame.K_s]:
            player_pos.y += 300 * dt
        if keys[pygame.K_a]:
            player_pos.x -= 300 * dt
        if keys[pygame.K_d]:
            player_pos.x += 300 * dt
        self.players[id] = player_pos

    async def game_loop(self):
        # poll for events
        while self.running:
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # get current pos
            player_pos = self.players.get(self.id, self.init_player_pos)

            # fill the screen with a color to wipe away anything from last frame
            self.screen.fill("purple")

            pygame.draw.circle(self.screen, "red", player_pos, 40)

            keys = pygame.key.get_pressed()
            print(
                f"w: {keys[pygame.K_w]}, a: {keys[pygame.K_a]}, s: {keys[pygame.K_s]}, d: {keys[pygame.K_d]}"
            )
            print(f"dt: {self.dt}")

            # await self.set_position(
            #     id=1,
            #     pos=self.players.get(1, self.init_player_pos),
            #     keys=keys,
            #     dt=self.dt,
            # )

            # calculate updated pos
            player_pos = await self.calc_position(
                pos=player_pos, keys=keys, dt=self.dt
            )  # this just prepares calculation

            # # post updated pos to server
            await self.send_position(pos=player_pos, websocket=self.websocket)

            # sync back to server
            self.players[self.id] = await self.receive_position(
                websocket=self.websocket
            )

            # flip() the display to put your work on screen
            pygame.display.flip()

            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            self.dt = self.clock.tick(60) / 1000

        pygame.quit()

    async def start_game(self):
        # pygame setup
        pygame.init()
        await self.game_loop()


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
        game = Game(server_address=SERVER_ADDRESS)

        # Attempt to send a message to the server
        asyncio.run(game.client_handler())

        # If successful, break out of the loop
        break

    except Exception as e:
        # If the connection fails, print the error and retry
        print(f"Connection failed: {e}. Retry...")
        # Optionally, remove the existing .env file before retrying
        create_dotenv(remove=True)

# Example file showing a circle moving on screen
import pygame
import os
from dotenv import load_dotenv
import websockets
from create_dotenv import create_dotenv
import asyncio
import json


class Player:
    def __init__(self, id, pos):
        self.id = id
        self.pos = pos
        self.color = "red"

    def set_pos(self, pos):
        self.pos = pos

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, 40)


class Game:
    def __init__(self, server_address):
        # server address
        self.server_address = server_address

        # game vars
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.init_player_pos = pygame.Vector2(
            self.screen.get_width() / 2, self.screen.get_height() / 2
        )

        # define intial player
        self.players = []

    async def get_session_id(self):
        while True:
            try:
                # get message
                message_text = await self.websocket.recv()
                # load message string to dict
                message = json.loads(message_text)
                type = message.get("type")
                if type == "new_connection":
                    return message.get("id")
                else:
                    continue

            except websockets.ConnectionClosed as e:
                print(f"Connection closed: {e.reason}")

    # calls send and receive message functions, and start the game
    async def client_handler(self):
        # connect to server
        async with websockets.connect(f"ws://{self.server_address}") as websocket:
            self.websocket = websocket
            # send and receive messages from the server asynchronously
            tasks = [
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
    async def send_position(self, id, pos, websocket):
        # while True:
        player_pos_x = pos.x
        player_pos_y = pos.y
        message = {
            "type": "player_move",
            "id": id,
            "pos_x": player_pos_x,
            "pos_y": player_pos_y,
        }
        await websocket.send(json.dumps(message))

    # receive position, continuously running proccess alongside the game
    async def receive_position(self, id, websocket):
        while True:
            try:
                # get message
                message_text = await websocket.recv()
                # load message string to dict
                message = json.loads(message_text)
                type = message.get("type")
                player_id = message.get("id")
                if (type == "player_move") and (int(player_id) == int(id)):
                    player_pos_x = message.get("pos_x")
                    player_pos_y = message.get("pos_y")
                    print(f"x: {player_pos_x}, y: {player_pos_x}")
                    return pygame.Vector2(player_pos_x, player_pos_y)
                else:
                    continue

            except websockets.ConnectionClosed as e:
                print(f"Connection closed: {e.reason}")

    async def game_loop(self):
        # init vars that can't be init in __init__ due to async
        self.session_id = await self.get_session_id()
        self.control_player = Player(id=self.session_id, pos=self.init_player_pos)
        self.players.append(self.control_player)

        # poll for events
        while self.running:
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # fill the screen with a color to wipe away anything from last frame
            self.screen.fill("purple")

            # draw each player
            for player in self.players:
                player.draw(screen=self.screen)

            keys = pygame.key.get_pressed()

            # calculate updated position for the player being controlled
            updated_player_pos = await self.calc_position(
                pos=self.control_player.pos, keys=keys, dt=self.dt
            )

            # post updated pos to server
            await self.send_position(
                id=self.control_player.id,
                pos=updated_player_pos,
                websocket=self.websocket,
            )

            # sync back to server
            for player in self.players:
                player.set_pos(
                    pos=await self.receive_position(
                        id=player.id, websocket=self.websocket
                    )
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

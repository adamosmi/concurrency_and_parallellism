# Example file showing a circle moving on screen
import pygame
import os
from dotenv import load_dotenv
import websockets
from create_dotenv import create_dotenv
import asyncio
import json


class GameManager:
    """
    Game context manager.
    Holds the connection to the websocket and queue for memory.
    The game instance is managed here to prevent the following error from attempting to call multiple async functions within the game loop:
    Connection failed: cannot call recv while another coroutine is already waiting for the next message. Retry...


    Order of operations:
        1) Read server to get server messages
        2) Add server messages to game queue
        3) Update game state
        4) Add game update messages to server queue
        5) Send server queue messages to server
    """

    def __init__(self, server_address):
        self.server_address = server_address
        self.game_in_queue = asyncio.Queue()
        self.game_out_queue = asyncio.Queue()

    async def manage_game(self):
        # define game instance
        self.game = Game(
            game_in_queue=self.game_in_queue, game_out_queue=self.game_out_queue
        )

        # connect to server
        async with websockets.connect(f"ws://{self.server_address}") as websocket:
            self.websocket = websocket
            # send and receive messages from the server asynchronously
            tasks = [
                self.get_messages(),  # move messages from server to game_in_queue
                self.game.process_in_queue(),  # continously look for new players, player movements in game_in_queue
                self.game.async_run_game(),  # run the game continously, outputing new player movements in to_game_out_queue list
                self.game.process_out_queue(),  # continously look for entries in to_game_out_queue and add to game_out_queue
                self.send_messages(),  # move messages from game_out_queue to server
            ]
            await asyncio.gather(*tasks)

    async def get_messages(self):
        """
        Listen for messages on server and add them to queue.
        """
        print("get_messages")
        while True:
            try:
                message_text = await self.websocket.recv()
                print(f"Message received from server: {message_text}")
                await self.game_in_queue.put(message_text)
                print(f"Message added to game_in_queue: {message_text}")
            except Exception as e:
                print(f"Exception: {e}")

    async def send_messages(self):
        """
        Listen for messages on queue and add them to server.
        """
        print("send_messages")
        while True:
            try:
                message_text = await self.game_out_queue.get()
                print(f"Message received from game_out_queue: {message_text}")
                # await self.game_out_queue.put(message_text)
                # print(f"Message added back to game_out_queue: {message_text}")
                await self.websocket.send(message_text)
                print(f"Message added to server: {message_text}")
            except Exception as e:
                print(f"Exception: {e}")


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
    def __init__(self, game_in_queue, game_out_queue):
        self.game_in_queue = game_in_queue
        self.game_out_queue = game_out_queue

        # game vars
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.init_player_pos = pygame.Vector2(
            self.screen.get_width() / 2, self.screen.get_height() / 2
        )

        # define intial player
        self.control_player = None
        self.players = {}

        # to game_out_queue
        self.to_game_out_queue = []

    async def process_out_queue(self):
        """
        Read game state and update queue
        """
        print("process_out_queue")
        while True:
            try:
                if len(self.to_game_out_queue) == 0:
                    await asyncio.sleep(self.dt)
                else:
                    message = self.to_game_out_queue.pop()
                    await self.game_out_queue.put(json.dumps(message))
                    print(f"Message added to game_out_queue: {json.dumps(message)}")

            except Exception as e:
                print(f"Exception: {e}")

    async def process_in_queue(self):
        """
        Read queue and update game state
        """
        print("process_in_queue")
        while True:
            try:
                message_text = await self.game_in_queue.get()
                print(f"Message received from game_in_queue: {message_text}")
                message = json.loads(message_text)
                message_type = message.get("type")
                # server generated messages
                if message_type == "new_connection":
                    await self.manage_new_connection_message(message)
                # client generated messages
                elif message_type == "player_move":
                    await self.manage_player_move_message(message)
                else:
                    continue

            except Exception as e:
                print(f"Exception: {e}")

    async def manage_new_connection_message(self, message):
        print("managing new connection")
        id = message.get("id")
        # check to see if control_player is set
        if self.control_player is None:
            # if not, set one
            self.control_player = Player(id=id, pos=self.init_player_pos)
            self.players[id] = self.control_player

        # check to see if other players joined the game
        if self.control_player.id == int(id):
            pass
        else:
            # if other player joined the game, add to self.players
            self.players[id] = Player(
                id=id, pos=self.init_player_pos
            )  # spawn at initial position, will be updated next frame

    async def manage_player_move_message(self, message):
        """
        "player_move" type messages only possible after "new_connection" type messages.
        """
        print("managing player move")
        id = message.get("id")
        player_pos_x = message.get("pos_x")
        player_pos_y = message.get("pos_y")
        player_ref = self.players[id]
        player_ref.pos = pygame.Vector2(player_pos_x, player_pos_y)
        self.players[id] = player_ref
        print(f"Position updated: id: {id}, x: {player_pos_x}, y: {player_pos_x}")

    def calc_position(self, pos, keys, dt):
        """
        Given a position and keys pressed, return new position.
        """
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
    def stage_position(self, id, pos):
        """
        Stage player postion to be sent.
        """
        print("send_position")
        player_pos_x = pos.x
        player_pos_y = pos.y
        message = {
            "type": "player_move",
            "id": id,
            "pos_x": player_pos_x,
            "pos_y": player_pos_y,
        }
        self.to_game_out_queue.append(message)

    def run_game(self):
        """
        Core game implementation.
        """
        print("game_loop")
        pygame.init()

        # poll for events
        while self.running:
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # fill the screen with a color to wipe away anything from last frame
            print("color screen")
            self.screen.fill("purple")

            # draw each player
            print("draw players")
            print(self.players)
            if len(self.players) > 0:
                for player in self.players.values():
                    print(f"Drawing player: {player.id}")
                    player.draw(screen=self.screen)

                print("press key")
                keys = pygame.key.get_pressed()
                print(
                    f"w: {keys[pygame.K_w]}, a: {keys[pygame.K_a]}, s: {keys[pygame.K_s]}, d: {keys[pygame.K_d]}"
                )

                print("calc updated position")
                # calculate updated position for the player being controlled
                updated_player_pos = self.calc_position(
                    pos=self.control_player.pos, keys=keys, dt=self.dt
                )

                # post updated pos to queue
                print("stage position")
                self.stage_position(id=self.control_player.id, pos=updated_player_pos)

            # sync back to queue happening in process_in_queue, async
            # new positions being loaded from server

            # flip() the display to put your work on screen
            pygame.display.flip()

            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            self.dt = self.clock.tick(1) / 1000

        pygame.quit()

    async def async_run_game(self):
        await asyncio.to_thread(self.run_game())


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
        game_manager = GameManager(server_address=SERVER_ADDRESS)

        # Attempt to send a message to the server
        asyncio.run(game_manager.manage_game())

        # If successful, break out of the loop
        break

    except Exception as e:
        # If the connection fails, print the error and retry
        print(f"Connection failed: {e}. Retry...")
        # Optionally, remove the existing .env file before retrying
        create_dotenv(remove=True)

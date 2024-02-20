import asyncio
import websockets

# track connected clients
connected = set()


async def broadcast(message):
    for websocket in connected:
        await websocket.send(message)


# handle connected clients
async def handler(websocket):
    # add the connected client
    connected.add(websocket)
    try:
        # listen for messages from websocket
        async for message in websocket:
            print(f"Message recieved:\n{message}")
            # broadcast any message received to
            await broadcast(message)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connected.remove(websocket)


# main
async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()


asyncio.run(main())

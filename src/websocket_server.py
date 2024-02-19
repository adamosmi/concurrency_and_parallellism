import asyncio
import websockets

# track connected clients
connected = set()


# handle connected clients
async def handler(websocket):
    # add the connected client
    connected.add(websocket)
    # listen for message from websocket
    message = await websocket.recv()
    # broadcast any message received to
    websockets.broadcast(websockets=connected, message=message)


# main
async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()


asyncio.run(main())

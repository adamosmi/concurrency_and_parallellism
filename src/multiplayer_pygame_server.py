import asyncio
import websockets
import json

# track connected clients
connected = {}


# send messages to all connected
async def broadcast(message):
    for websocket in connected.values():
        await websocket.send(message)


# handle connected clients
async def handler(websocket):
    # assign id to new connection
    if len(connected) == 0:
        id = 1
    else:
        id = max(connected.keys()) + 1

    # add the connected client
    connected[id] = websocket

    # send id back to newly connected client
    new_connection_message = {"type": "new_connection", "id": id}
    await websocket.send(json.dumps(new_connection_message))

    try:
        # listen for messages from websocket
        async for message in websocket:
            print(f"Message recieved:\n{message}")
            # broadcast any message received to
            await broadcast(message)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connected.pop(id)


# main
async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()


asyncio.run(main())

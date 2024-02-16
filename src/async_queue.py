import asyncio
import random
import time


# # put items option 1: has to wait for each number i to be generated
# async def put_items(queue):
#     for i in range(5):
#         await queue.put(i)
#         print(f"Item {i} put in queue")
#     # Put a sentinel value in the queue to indicate the producer is done
#     await queue.put(None)


# put items option 2: asyncronously generates data
async def produce_item(queue, i):
    r = random.randrange(0, 2)
    if r > 0:
        print(f"Item {i} is sleeping for {r} second(s)")
        await asyncio.sleep(r)
    await queue.put(i)
    print(f"Item {i} put in queue")


async def put_items(queue):
    # Create a list of producer coroutines
    producers = [produce_item(queue, i) for i in range(5)]
    # Await their completion
    await asyncio.gather(*producers)
    # Put a sentinel value in the queue to indicate the producer is done
    await queue.put(None)


async def get_items(queue):
    while True:
        i = await queue.get()
        if i is None:
            # If we get the sentinel value, break out of the loop
            break
        print(f"Item {i} got from queue")


async def main():
    queue = asyncio.Queue()
    # Run the producer and consumer tasks concurrently
    await asyncio.gather(put_items(queue), get_items(queue))


# Run the main coroutine
t = time.perf_counter()
asyncio.run(main())
print(f"Time: {time.perf_counter() - t}")
# Time: 1.0048635059974913

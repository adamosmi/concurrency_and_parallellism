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
    producers = [produce_item(queue, i) for i in range(10)]
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

# (venv) andrew@DESKTOP-M43FL6J:/mnt/nfs/Projects/Concurrency_and_Parallellism$ python3 ./src/async_queue.py
# Item 0 put in queue
# Item 1 is sleeping for 1 second(s)
# Item 2 is sleeping for 1 second(s)
# Item 3 put in queue
# Item 4 put in queue
# Item 5 is sleeping for 1 second(s)
# Item 6 put in queue
# Item 7 put in queue
# Item 8 put in queue
# Item 9 is sleeping for 1 second(s)
# Item 0 got from queue
# Item 3 got from queue
# Item 4 got from queue
# Item 6 got from queue
# Item 7 got from queue
# Item 8 got from queue
# Item 1 put in queue
# Item 2 put in queue
# Item 5 put in queue
# Item 9 put in queue
# Item 1 got from queue
# Item 2 got from queue
# Item 5 got from queue
# Item 9 got from queue
# Time: 1.00401709200014

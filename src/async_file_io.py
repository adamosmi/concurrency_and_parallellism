import asyncio
import aiofiles
import random


# async def read_from_file(filename):
#     async with aiofiles.open(filename, mode="r") as file:
#         while True:
#             await asyncio.sleep(random.random())
#             content = await file.readline()
#             print(f"reading: {content}")


async def read_from_file(filename):
    while True:
        async with aiofiles.open(filename, mode="r") as file:
            # Read the entire file
            content = await file.read()
            if content:
                print(f"reading: {content}")
            else:
                print("No new data. Waiting for new data...")
        # Wait a bit before reopening the file to check for new data
        await asyncio.sleep(random.random())


async def generate_data(n):
    """
    Genereates an int 1 through n.
    """
    await asyncio.sleep(random.random())
    data = random.randint(1, n)
    return data


async def put_data(queue):
    while True:
        data = await generate_data(100)
        await queue.put(data)
        # print(f"put: {data}")


async def get_data(queue):
    while True:
        data = await queue.get()
        print(f"get: {data}")


async def write_to_file(queue, filename):
    async with aiofiles.open(filename, mode="a+") as file:
        while True:
            data = await queue.get()
            await file.write(str(data) + "\n")
            print(f"writing: {data}")


async def async_main():
    # with open("data/example.txt", "w") as file:
    #     file.write("First Line \n")
    queue = asyncio.Queue()
    tasks = [
        put_data(queue),
        # get_data(queue),
        write_to_file(queue, "data/example.txt"),
        read_from_file("data/example.txt"),
    ]
    await asyncio.gather(*tasks)


# Example usage
asyncio.run(async_main())

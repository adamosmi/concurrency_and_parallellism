import asyncio
import aiofiles
import random


async def read_from_file(filename):
    async with aiofiles.open(filename, mode="r") as file:
        content = await file.read()
        print(f"Content of {filename}:")
        print(content)


async def generate_data(n):
    """
    Genereates an int 1 through n.
    """
    # r = random.randint(0, 1)
    # if r == 1:
    #     await asyncio.sleep(1)
    data = random.randint(1, n + 1)
    return data


async def put_data(queue):
    while True:
        data = await generate_data(10)
        await queue.put(data)
        print(f"put: {data}")


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
    queue = asyncio.Queue()
    tasks = [
        read_from_file("data/example.txt"),
        put_data(queue),
        write_to_file(queue, "data/example.txt"),
    ]
    await asyncio.gather(*tasks)


# Example usage
asyncio.run(async_main())

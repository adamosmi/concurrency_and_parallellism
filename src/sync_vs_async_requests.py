import requests
import aiohttp
import asyncio
import time

# Define a list of URLs to be fetched
URLS = [
    "http://httpbin.org/delay/1",
    "http://httpbin.org/delay/2",
    "http://httpbin.org/delay/3",
]


# Synchronous requests using requests library
def fetch_sync(url):
    print(f"Starting {url}")
    response = requests.get(url)
    print(f"Finished {url}")


def run_sync():
    for url in URLS:
        fetch_sync(url)


# Asynchronous requests using aiohttp and asyncio
async def fetch_async(session, url):
    print(f"Starting {url}")
    async with session.get(url) as response:
        await response.read()
        print(f"Finished {url}")


async def run_async():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_async(session, url) for url in URLS]
        await asyncio.gather(*tasks)


# Timing the synchronous function
start_time = time.time()
run_sync()
end_time = time.time()
print(f"Synchronous version took {end_time - start_time} seconds.")

# Timing the asynchronous function
start_time = time.time()
asyncio.run(run_async())
end_time = time.time()
print(f"Asynchronous version took {end_time - start_time} seconds.")

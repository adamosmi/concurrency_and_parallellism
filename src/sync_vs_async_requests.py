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
    _ = requests.get(url)
    print(f"Finished {url}")


# Run the synchronous process
def run_sync():
    for url in URLS:
        fetch_sync(url)


# Asynchronous requests using aiohttp and asyncio
async def fetch_async(session, url):
    print(f"Starting {url}")
    async with session.get(url) as response:
        await response.read()
        print(f"Finished {url}")


# Run the asynchronous process
async def run_async():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_async(session, url) for url in URLS]
        await asyncio.gather(*tasks)


# Timing the synchronous function
start_time = time.perf_counter()
run_sync()
end_time = time.perf_counter()
print(f"Synchronous version took {end_time - start_time} seconds.")
# Synchronous version took 6.5700838820011995 seconds.


# Timing the asynchronous function
start_time = time.perf_counter()
asyncio.run(run_async())
end_time = time.perf_counter()
print(f"Asynchronous version took {end_time - start_time} seconds.")
# Asynchronous version took 3.2167510360013694 seconds.

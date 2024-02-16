import time
import threading
import multiprocessing
import asyncio


def sleep(i=1):
    print(f"start: #{i}")
    time.sleep(1)
    print(f"end: #{i}")


async def sleep_async(i=1):
    print(f"start: #{i}")
    await asyncio.sleep(1)
    print(f"end: #{i}")


# 3 seconds - sequential
print("3 in a row")
sleep()
sleep()
sleep()

# 1 second - one call
print("1 async call")
asyncio.run(sleep_async())

# threading
print("10 threading calls")
n = 10
threads = []
for i in range(n):
    # start timer
    rt = time.perf_counter()
    # add function calls n times, n = # loops
    t = threading.Thread(target=sleep, args=(i,))
    threads.append(t)
    t.start()

for thread in threads:
    thread.join()

    # everything after here (after the join) runs synchronously
    print(f"time elapsed {time.perf_counter() - rt}")

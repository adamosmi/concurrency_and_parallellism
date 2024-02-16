import time
import threading
import multiprocessing
import asyncio


# defined workloads
# sync
def sleep(i=1):
    print(f"start: #{i}")
    time.sleep(1)
    print(f"end: #{i}")


# async
async def sleep_async(i=1):
    print(f"start: #{i}")
    await asyncio.sleep(1)
    print(f"end: #{i}")


# 3 seconds - sequential
print("3 in a row")
sleep()  # 1 second each
sleep()
sleep()
# 3 seconds


# 1 second - one call
print("1 async call")
asyncio.run(sleep_async())

# 1 second - threading
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


# asyncio
# 1 second
async def asyncio_main():
    rt = time.perf_counter()
    await asyncio.gather(*[sleep_async(i) for i in range(10)])
    print(f"time elapsed {time.perf_counter() - rt}")


print("10 async (coroutine) calls")
asyncio.run(asyncio_main())


# processing
# 1 second
print("10 processing calls")
n = 10
processes = []
for i in range(n):
    # start timer
    rt = time.perf_counter()
    # add function calls n times, n = # loops
    p = multiprocessing.Process(target=sleep, args=(i,))
    processes.append(p)
    p.start()
for process in processes:
    process.join()
    # everything after here (after the join) runs synchronously
    print(f"time elapsed {time.perf_counter() - rt}")

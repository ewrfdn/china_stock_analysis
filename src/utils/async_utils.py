import asyncio
import nest_asyncio

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        nest_asyncio.apply()  # allow nested event loops
        future = asyncio.ensure_future(coro)
        loop.run_until_complete(future)
        return future.result()
    else:
        return asyncio.run(coro)

async def async_run_all(method, param_list, concurrency):
    sem = asyncio.Semaphore(concurrency)

    async def run_with_sem(params):
        async with sem:
            return await method(*params)

    tasks = [asyncio.create_task(run_with_sem(p)) for p in param_list]
    return await asyncio.gather(*tasks)


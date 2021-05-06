import contextlib
import asyncio


if hasattr(asyncio, "get_running_loop"):
    get_running_loop = asyncio.get_running_loop
else:  # < 3.7, may be unsafe outside coroutines (running loop)
    get_running_loop = asyncio.get_event_loop  # pragma: no cover


if hasattr(asyncio, "create_task"):
    create_task = asyncio.create_task
else: # < 3.7, totally unsafe outside loop
    def create_task(coro):  # pragma: no cover
        return asyncio.get_event_loop().create_task(coro)
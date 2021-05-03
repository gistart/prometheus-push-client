import asyncio

if hasattr(asyncio, "get_running_loop"):
    get_running_loop = asyncio.get_running_loop
else:  # < 3.7, may be unsafe outside coroutines
    get_running_loop = asyncio.get_event_loop

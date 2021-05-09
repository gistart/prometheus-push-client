import asyncio
try:
    import requests
except ImportError:  # pragma: no cover
    requests = None
try:
    import aiohttp
except ImportError:  # pragma: no cover
    aiohttp = None


class BaseHttpTransport:
    def __init__(self, url):
        self._validate()
        self.url = url
        self.session = None

    def _validate(self):  # pragma: no cover
        pass

    def push_all_sync(self):
        raise NotImplementedError("brave proposal")


# TODO: configurable push formats ?


class SyncHttpTransport(BaseHttpTransport):
    def _validate(self):
        if requests is None:
            raise RuntimeError("`requests` package is required")

    def start(self):
        self.session = requests.Session()

    def stop(self):
        self.session.close()

    def push_all(self, iterable):
        data = b"\n".join(iterable)
        self.session.post(self.url, data=data)


class AioHttpTransport(BaseHttpTransport):
    def _validate(self):
        if aiohttp is None:
            raise RuntimeError("`aiohttp` package is required")

    async def start(self):
        self.session = aiohttp.ClientSession()

    async def stop(self):
        await self.session.close()

    async def push_all(self, iterable):
        data = b"\n".join(iterable)
        async with self.session.post(self.url, data=data) as _:
            pass
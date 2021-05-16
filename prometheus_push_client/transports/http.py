try:
    import requests
except ImportError:  # pragma: no cover
    requests = None
try:
    import aiohttp
except ImportError:  # pragma: no cover
    aiohttp = None


class BaseHttpTransport:
    def __init__(self, url, verb="POST"):
        self._validate()
        self.url = url
        self.verb = verb
        self.session = None
        #TODO: basic auth, custom headers, tls ?

    def _validate(self):  # pragma: no cover
        pass

    def prepare_data(self, iterable):
        data = b"\n".join(iterable)
        if data.endswith(b"\n\n"):  # pragma: no cover
            return data
        to_pad = 1 if data[-1] == ord(b"\n") else 2
        return data.ljust(len(data) + to_pad, b"\n")

    def push_all_sync(self):
        raise NotImplementedError("brave proposal")


class SyncHttpTransport(BaseHttpTransport):
    def _validate(self):
        if requests is None:
            raise RuntimeError("`requests` package is required")

    def start(self):
        self.session = requests.Session()

    def stop(self):
        self.session.close()

    def push_all(self, iterable):
        data = self.prepare_data(iterable)
        self.session.request(self.verb, self.url, data=data)


class AioHttpTransport(BaseHttpTransport):
    def _validate(self):
        if aiohttp is None:
            raise RuntimeError("`aiohttp` package is required")

    async def start(self):
        self.session = aiohttp.ClientSession()

    async def stop(self):
        await self.session.close()

    async def push_all(self, iterable):
        data = self.prepare_data(iterable)
        async with self.session.request(self.verb, self.url, data=data) as _:
            pass
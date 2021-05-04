"""
For documentation purposes
"""


class BaseSyncTransport:  # pragma: no cover
    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def push_all(self, iterable):
        raise NotImplementedError()


class BaseAsyncTransport:  # pragma: no cover
    async def start(self):
        raise NotImplementedError()

    async def stop(self):
        raise NotImplementedError()

    async def push_all(self, iterable):
        raise NotImplementedError()
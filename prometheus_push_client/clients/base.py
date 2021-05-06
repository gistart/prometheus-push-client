"""
For documentation purposes
"""


class BaseSyncClient:  # pragma: no cover
    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()


class BaseAsyncClient:  # pragma: no cover
    async def start(self):
        raise NotImplementedError()

    async def stop(self):
        raise NotImplementedError()
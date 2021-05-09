import functools

import prometheus_push_client as ppc


def influx_udp_async(host, port, period=15.0, registry=ppc.PUSH_REGISTRY):
    client = ppc.AsyncBatchClient(
        format=ppc.InfluxFormat(registry=registry),
        transport=ppc.AioUdpTransport(host, port),
        period=period,
    )
    return _async_wrap(client)


def influx_udp_thread(host, port, period=15.0, registry=ppc.PUSH_REGISTRY):
    client = ppc.ThreadBatchClient(
        format=ppc.InfluxFormat(registry=registry),
        transport=ppc.SyncUdpTransport(host, port),
        period=period,
    )
    return _sync_wrap(client)


def influx_http_async(url, period=15.0, registry=ppc.PUSH_REGISTRY):
    client = ppc.AsyncBatchClient(
        format=ppc.InfluxFormat(registry=registry),
        transport=ppc.AioHttpTransport(url),
        period=period,
    )
    return _async_wrap(client)


def influx_http_thread(url, period=15.0, registry=ppc.PUSH_REGISTRY):
    client = ppc.ThreadBatchClient(
        format=ppc.InfluxFormat(registry=registry),
        transport=ppc.SyncHttpTransport(url),
        period=period,
    )
    return _sync_wrap(client)


def statsd_udp_async(host, port, period=15.0, registry=ppc.PUSH_REGISTRY):
    client = ppc.AsyncBatchClient(
        format=ppc.StatsdFormat(registry=registry),
        transport=ppc.AioUdpTransport(host, port),
        period=period,
    )
    return _async_wrap(client)


def statsd_udp_thread(host, port, period=15.0, registry=ppc.PUSH_REGISTRY):
    client = ppc.ThreadBatchClient(
        format=ppc.StatsdFormat(registry=registry),
        transport=ppc.SyncUdpTransport(host, port),
        period=period,
    )
    return _sync_wrap(client)


def influx_udp_aiostream(host, port, registry=ppc.PUSH_REGISTRY):
    client = ppc.AsyncStreamingClient(
        format=ppc.InfluxFormat(registry=registry),
        transport=ppc.AioUdpTransport(host, port)
    )
    return _async_wrap(client)


def influx_udp_stream(host, port, registry=ppc.PUSH_REGISTRY):
    client = ppc.SyncStreamingClient(
        format=ppc.InfluxFormat(registry=registry),
        transport=ppc.SyncUdpTransport(host, port)
    )
    return _sync_wrap(client)


def statsd_udp_aiostream(host, port, registry=ppc.PUSH_REGISTRY):
    client = ppc.AsyncStreamingClient(
        format=ppc.StatsdFormat(registry=registry),
        transport=ppc.AioUdpTransport(host, port),
    )
    return _async_wrap(client)


def statsd_udp_stream(host, port, registry=ppc.PUSH_REGISTRY):
    client = ppc.SyncStreamingClient(
        format=ppc.StatsdFormat(registry=registry),
        transport=ppc.SyncUdpTransport(host, port),
    )
    return _sync_wrap(client)


#
# decorator AND context manager
#


class _sync_wrap:
    def __init__(self, client):
        self.client = client
        self._entered = 0  # recursive calls of decorated function

    def __call__(self, func):
        @functools.wraps(func)
        def _wrap_call(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return _wrap_call

    def __enter__(self):
        if self._entered == 0:
            self.client.start()
        self._entered += 1
        return self

    def __exit__(self, *exc_info):
        self._entered -= 1
        if self._entered == 0:
            self.client.stop()
        return False


class _async_wrap:
    def __init__(self, client):
        self.client = client
        self._entered = 0  # recursive calls of decorated function

    def __call__(self, func):
        @functools.wraps(func)
        async def _wrap_call(*args, **kwargs):
            async with self:
                return await func(*args, **kwargs)
        return _wrap_call

    async def __aenter__(self):
        if self._entered == 0:
            await self.client.start()
        self._entered += 1
        return self

    async def __aexit__(self, *exc_info):
        self._entered -= 1
        if self._entered == 0:
            await self.client.stop()
        return False
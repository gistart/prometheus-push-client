import functools

import prometheus_push_client as ppc


def _thread_bg(client):
    def _wrap_func(func):
        @functools.wraps(func)
        def _wrap_call(*args, **kwargs):
            client.start()
            try:
                return func(*args, **kwargs)
            finally:
                client.stop()
        return _wrap_call
    return _wrap_func


def _async_bg(client):
    def _wrap_func(func):
        @functools.wraps(func)
        async def _wrap_call(*args, **kwargs):
            await client.start()
            try:
                return await func(*args, **kwargs)
            finally:
                await client.stop()
        return _wrap_call
    return _wrap_func


def influx_udp_async(host, port, period=15.0):
    client = ppc.AsyncioBGClient(
        format=ppc.InfluxFormat(),
        transport=ppc.AioUdpTransport(host, port),
        period=period,
    )
    return _async_bg(client)


def influx_udp_thread(host, port, period=15.0):
    client = ppc.ThreadBGClient(
        format=ppc.InfluxFormat(),
        transport=ppc.SyncUdpTransport(host, port),
        period=period,
    )
    return _thread_bg(client)


def graphite_udp_async(host, port, period=15.0):
    client = ppc.AsyncioBGClient(
        format=ppc.GraphiteFormat(),
        transport=ppc.AioUdpTransport(host, port),
        period=period,
    )
    return _async_bg(client)


def graphite_udp_thread(host, port, period=15.0):
    client = ppc.ThreadBGClient(
        format=ppc.GraphiteFormat(),
        transport=ppc.SyncUdpTransport(host, port),
        period=period,
    )
    return _thread_bg(client)
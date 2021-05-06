import pytest
import sys
import time
import asyncio
import logging
import string

import prometheus_push_client as ppc
from prometheus_push_client import compat
from prometheus_push_client.transports.udp import BaseUdpTransport
from prometheus_push_client.decorators import _sync_wrap


def test_missing_requests(mocker):
    mocker.patch("prometheus_push_client.transports.http.requests", None)
    with pytest.raises(RuntimeError):
        ppc.SyncHttpTransport("")


def test_missing_aiohttp(mocker):
    mocker.patch("prometheus_push_client.transports.http.aiohttp", None)
    with pytest.raises(RuntimeError):
        ppc.AioHttpTransport("")


def test_thread_client_transport_crash(mocker, caplog):
    mocker.patch(
        "prometheus_push_client.transports.udp.SyncUdpTransport.push_all",
        new=lambda *args, **kwargs: 1 / 0
    )

    @ppc.influx_udp_thread("localhost", 9876, 0.1)
    def _test():
        for i in range(3):
            time.sleep(0.1)

    with caplog.at_level(logging.INFO):
        _test()

    assert any(
        lr.name == "prometheus.batch" and
        lr.msg == "push crashed" and
        (lr.exc_info is None or lr.exc_info[0] is ZeroDivisionError)
        for lr in caplog.records
    )


@pytest.mark.asyncio
async def test_async_client_transport_crash(mocker, caplog):
    mocker.patch(
        "prometheus_push_client.transports.udp.AioUdpTransport.push_all",
        new=lambda *args, **kwargs: 1 / 0
    )

    @ppc.influx_udp_async("localhost", 9876, 0.1)
    async def _test():
        for i in range(3):
            await asyncio.sleep(0.1)

    with caplog.at_level(logging.INFO):
        await _test()

    assert any(
        lr.name == "prometheus.batch" and
        lr.msg == "push crashed" and
        (lr.exc_info is None or lr.exc_info[0] is ZeroDivisionError)
        for lr in caplog.records
    )


# len(ALL_BYTES) == 2920
ALL_BYTES = b"".join(
    (
        string.ascii_letters +
        string.ascii_uppercase +
        string.ascii_uppercase +
        string.digits +
        string.punctuation
    ).encode("utf8")
    for _ in range(20)
)


def _gen_datagram(line_len, n_lines):
    for _ in range(n_lines):
        yield ALL_BYTES[:line_len]


@pytest.mark.parametrize("mtu,dg_lines,expected,to_pack", [
    # bytes
    (500, 99,  1, _gen_datagram(  10, 10)),
    (500, 99,  3, _gen_datagram( 100, 10)),

    # lines
    (500,  1, 10, _gen_datagram(   1, 10)),
    (500,  2,  5, _gen_datagram(   1, 10)),

    # newlines
    (503, 99,  3, _gen_datagram( 100, 10)),
    (504, 99,  2, _gen_datagram( 100, 10)),

    # long lines
    (  1, 99, 10, _gen_datagram(1000, 10)),

    # ver length
    (10, 99, 2, (b"123456", b"7890")),
    (10, 99, 2, (b"7890", b"123456")),
    (10, 99, 2, (b"123456789", b"0")),
    (10, 99, 2, (b"0", b"123456789")),

    (10, 99, 2, (b"0", b"1", b"23456789-")),
    (10, 99, 2, (b"012345678", b"9", b"-")),
    (10, 99, 3, (b"0", b"123456789", b"-")),

])
def test_datagram_packer(mtu, dg_lines, expected, to_pack):
    transport = BaseUdpTransport("", -1, mtu=mtu, datagram_lines=dg_lines)
    for i, datagram in enumerate(transport.pack_datagrams(to_pack)):
        lines = datagram.split(b"\n")
        assert (
            len(lines) == 1 or  # metrics longer than mtu
            (
                1 < len(lines) <= dg_lines and
                0 < len(datagram) <= mtu
            )
        )

    assert i + 1 == expected


def test_decorator_context():
    class MockClient:
        def start(self): pass
        def stop(self): pass

    wrap = _sync_wrap(MockClient())

    @wrap
    def _test(n):
        if n == 0:
            return wrap._entered
        with wrap:  # same wrapper again
            return _test(n - 1)

    recursions = 10
    assert wrap._entered == 0
    assert _test(recursions) == 2 * recursions + 1  # +1 initial call
    assert wrap._entered == 0
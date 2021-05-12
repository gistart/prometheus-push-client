import pytest
import logging
import socket

import prometheus_push_client as ppc


def test_sync_udp_gaierror(caplog):
    transport = ppc.SyncUdpTransport("X-does-not-exist-X-123", 1)
    with caplog.at_level(logging.INFO):
        transport.start()

    assert any(
        lr.name == "prometheus.udp" and
        any(isinstance(a, socket.gaierror) for a in lr.args)
        for lr in caplog.records
    )

    # does not raise
    transport.push_all([b"1", b"2"])


@pytest.mark.asyncio
async def test_async_udp_gaierror(caplog):
    transport = ppc.AioUdpTransport("X-does-not-exist-X-123", 1)
    with caplog.at_level(logging.INFO):
        await transport.start()

    assert any(
        lr.name == "prometheus.udp" and
        any(isinstance(a, socket.gaierror) for a in lr.args)
        for lr in caplog.records
    )

    # does not raise
    await transport.push_all([b"1", b"2"])
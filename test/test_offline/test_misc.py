import pytest
import sys
import time
import asyncio
import logging

import prometheus_push_client as ppc
from prometheus_push_client import compat


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
        "prometheus_push_client.transports.udp.BaseUdpTransport.push_all",
        new=lambda *args, **kwargs: 1 / 0
    )

    @ppc.influx_udp_thread("localhost", 9876, 0.1)
    def _test():
        for i in range(3):
            time.sleep(0.1)

    with caplog.at_level(logging.INFO):
        _test()

    assert any(
        lr.name == "prometheus.bg" and lr.msg == "push crashed"
        for lr in caplog.records
    )


@pytest.mark.asyncio
async def test_thread_client_transport_crash(mocker, caplog):
    mocker.patch(
        "prometheus_push_client.transports.udp.BaseUdpTransport.push_all",
        new=lambda *args, **kwargs: 1 / 0
    )

    @ppc.influx_udp_async("localhost", 9876, 0.1)
    async def _test():
        for i in range(3):
            await asyncio.sleep(0.1)

    with caplog.at_level(logging.INFO):
        await _test()

    assert any(
        lr.name == "prometheus.bg" and lr.msg == "push crashed"
        for lr in caplog.records
    )
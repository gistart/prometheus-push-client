import asyncio
from collections import namedtuple
import math
import time
import pytest
import requests

import prometheus_push_client as ppc

from testutils import make_metric_fixture, collect_metrics


NS = "test_statsd"


def get_metrics(cfg):
    response = requests.get(cfg.statsd_url)
    content = response.text

    assert response.status_code == 200, content
    assert len(content), content

    return content


def test_ping(cfg):
    assert get_metrics(cfg)


@pytest.fixture(scope="module")  #! important
def hist1(request):
    return make_metric_fixture(request, ppc.Histogram(
        name="h1",
        namespace=NS,
        subsystem="statsd_udp",
        unit="meters",
        buckets=[0.05, 0.10, 0.15, 0.20, 0.25, 0.5, 1.0, float("inf")],
        labelnames=["l1"],
    ))



def test_statsd_udp_thread(cfg, hist1):

    for i in range(1, 251):
        hist1.labels(l1=1).observe(i / 100)

    period = 0.3
    sleeps = 2
    sleep_sec = 1.1
    samples_expected = math.ceil(sleeps / period)  # + graceful

    @ppc.statsd_udp_thread(cfg.statsd_host, cfg.statsd_udp_port, period)
    def _test():
        for i in range(1, sleeps + 1):
            hist1.labels(l1=2).observe(i / 10)
            time.sleep(sleep_sec)
        return 1 / 0

    with pytest.raises(ZeroDivisionError):
        _test()

    time.sleep(2.0)  # wait remote sync

    local_res = collect_metrics(hist1._name)
    local_res_lines = sorted(local_res.split("\n"))

    remote_all = get_metrics(cfg)
    remote_res = collect_metrics(hist1._name, data=remote_all)
    remote_res_lines = sorted(remote_res.split("\n"))

    assert len(local_res_lines) == len(remote_res_lines), remote_res
    for loc, rem in zip(local_res_lines, remote_res_lines):
        assert (
            loc == rem or
            loc.startswith(f"{rem}.")  # statsd-side float -> int
        )


@pytest.mark.asyncio
async def test_statsd_udp_asyncio(cfg, hist1):
    for i in range(1, 251):
        hist1.labels(l1=1).observe(i / 100)

    period = 0.3
    sleeps = 2
    sleep_sec = 1.1
    samples_expected = math.ceil(sleeps / period)  # + graceful

    @ppc.statsd_udp_async(cfg.statsd_host, cfg.statsd_udp_port, period)
    async def _test():
        for i in range(1, sleeps + 1):
            hist1.labels(l1=2).observe(i / 10)
            await asyncio.sleep(sleep_sec)
        return 1 / 0

    with pytest.raises(ZeroDivisionError):
        await _test()

    await asyncio.sleep(2.0)  # wait remote sync

    local_res = collect_metrics(hist1._name)
    local_res_lines = sorted(local_res.split("\n"))

    remote_all = get_metrics(cfg)
    remote_res = collect_metrics(hist1._name, data=remote_all)
    remote_res_lines = sorted(remote_res.split("\n"))

    assert len(local_res_lines) == len(remote_res_lines), remote_res
    for loc, rem in zip(local_res_lines, remote_res_lines):
        assert (
            loc == rem or
            loc.startswith(f"{rem}.")  # statsd-side float -> int
        )
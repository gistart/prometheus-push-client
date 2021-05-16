import asyncio
from collections import namedtuple
import time
import pytest
import requests

import re

import prometheus_push_client as ppc

from testutils import make_metric_fixture, collect_metrics


NS = "test_pushgw"
JOB = f"job/{NS}"

RX_JOB_TAG = re.compile(r"(job=\".*?\",?)")
RX_INSTANCE_TAG = re.compile(r"(instance=\".*?\",?)")


def get_metrics(cfg):
    response = requests.get(cfg.pushgw_url)
    content = response.text

    assert response.status_code == 200, content
    assert len(content), content

    return content


def test_ping(cfg):
    assert get_metrics(cfg)



@pytest.fixture
def summ1(request):
    return make_metric_fixture(request, ppc.Summary(
        name="summ1",
        namespace=NS,
        unit="seconds",
        labelnames=["l"],
    ))


@pytest.fixture
def gauge1(request):
    return make_metric_fixture(request, ppc.Gauge(
        name="gauge1",
        namespace=NS,
        unit="meters",
        labelnames=["l"],
    ))


def test_pushgateway_http_sync(cfg, summ1, gauge1):
    period = 0.4
    sleeps = 2
    sleep_sec = 1.0

    @ppc.openmetrics_http_thread(f"{cfg.pushgw_url}/{JOB}", period=period)
    def _test():
        for _ in range(sleeps):
            with gauge1.labels("L1").track_inprogress():
                with summ1.labels("L2").time():
                    time.sleep(sleep_sec)
        return 1 / 0   # testing graceful stop

    with pytest.raises(ZeroDivisionError):
        _test()

    time.sleep(1.0)  # let them sync

    local_res = collect_metrics(summ1._name, gauge1._name)
    local_res_lines = sorted(local_res.split("\n"))

    remote_all = get_metrics(cfg)
    remote_res = collect_metrics(summ1._name, gauge1._name, data=remote_all)

    remote_res_lines = []
    for rem_line in sorted(remote_res.split("\n")):
        rem_line = RX_INSTANCE_TAG.sub("", rem_line)
        rem_line = RX_JOB_TAG.sub("", rem_line)
        remote_res_lines.append(rem_line)

    assert len(local_res_lines) == len(remote_res_lines), remote_res
    for loc, rem in zip(local_res_lines, remote_res_lines):
        assert (
            loc == rem or
            loc.startswith(f"{rem}.")  # pushgw-side float -> int
        )


@pytest.mark.asyncio
async def test_pushgateway_http_sync(cfg, summ1, gauge1):
    period = 0.4
    sleeps = 2
    sleep_sec = 1.0

    async def _test():
        async with ppc.openmetrics_http_async(f"{cfg.pushgw_url}/{JOB}", period=period):
            for _ in range(sleeps):
                with gauge1.labels("L1").track_inprogress():
                    with summ1.labels("L2").time():
                        await asyncio.sleep(sleep_sec)
        return 1 / 0   # testing graceful stop

    with pytest.raises(ZeroDivisionError):
        await _test()

    await asyncio.sleep(1.0)  # let them sync

    local_res = collect_metrics(summ1._name, gauge1._name)
    local_res_lines = sorted(local_res.split("\n"))

    remote_all = get_metrics(cfg)
    remote_res = collect_metrics(summ1._name, gauge1._name, data=remote_all)

    remote_res_lines = []
    for rem_line in sorted(remote_res.split("\n")):
        rem_line = RX_INSTANCE_TAG.sub("", rem_line)
        rem_line = RX_JOB_TAG.sub("", rem_line)
        remote_res_lines.append(rem_line)

    assert len(local_res_lines) == len(remote_res_lines), remote_res
    for loc, rem in zip(local_res_lines, remote_res_lines):
        assert (
            loc == rem or
            loc.startswith(f"{rem}.")  # pushgw-side float -> int
        )
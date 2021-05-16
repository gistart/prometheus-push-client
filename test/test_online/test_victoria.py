import pytest
import json
import time
import math
import asyncio
import requests
from collections import Counter

import prometheus_push_client as ppc

from testutils import make_metric_fixture


NS = "test_vic"


def export(cfg, pattern=NS):
    response = requests.get(
        cfg.vm_export_url,
        params={'match[]': r'{__name__=~"%s.*"}' % pattern}
    )

    found = []
    for line in response.iter_lines():
        metric = json.loads(line)
        found.append(metric)
    return found


def count_samples(found, pattern):
    n_samples = Counter()
    for metric in found:
        mname = metric["metric"]["__name__"]
        if mname.startswith(pattern):
            n_samples[mname] += len(metric["values"])
    return n_samples


# TODO: get_last_value(found, pattern)


def test_ping(cfg):
    response = requests.get(cfg.vm_ping_url)
    content = response.text

    assert response.status_code == 200, content
    assert content == "OK", content


@pytest.fixture
def counter1(request):
    return make_metric_fixture(
        request,
        ppc.Counter("c1", namespace=NS, subsystem="influx_udp")
    )


def test_vic_influx_udp_thread(cfg, counter1):
    found_before = export(cfg)
    count_before = count_samples(found_before, counter1._name)

    period = 0.4
    sleeps = 2
    sleep_sec = 1.0
    samples_expected = math.ceil((sleeps * sleep_sec) / period)  # + graceful one
    assert samples_expected > 0

    def _test():
        for _ in range(sleeps):
            counter1.inc()
            time.sleep(sleep_sec)
        return 1 / 0   # testing graceful stop

    with pytest.raises(ZeroDivisionError):
        with ppc.influx_udp_thread(cfg.vm_host, cfg.vm_influx_port, period=period):
            _test()

    time.sleep(3.0)  # let them sync

    found_after = export(cfg)
    count_after = count_samples(found_after, counter1._name)

    for k in count_after.keys():
        assert samples_expected == count_after[k] - count_before[k]


@pytest.mark.asyncio
async def test_vic_influx_udp_async(cfg, counter1):
    found_before = export(cfg)
    count_before = count_samples(found_before, counter1._name)

    period = 0.3
    sleeps = 5
    sleep_sec = 0.2
    samples_expected = math.ceil((sleeps * sleep_sec) / period)  # + graceful one
    assert samples_expected > 0

    @ppc.influx_udp_async(cfg.vm_host, cfg.vm_influx_port, period=period)
    async def _test():
        for _ in range(sleeps):
            counter1.inc()
            await asyncio.sleep(sleep_sec)
        return 1 / 0   # testing graceful stop

    with pytest.raises(ZeroDivisionError):
        await _test()

    await asyncio.sleep(3.0)  # let them sync

    found_after = export(cfg)
    count_after = count_samples(found_after, counter1._name)

    for k in count_after.keys():
        assert samples_expected == count_after[k] - count_before[k]


def test_vic_influx_http_thread(cfg, counter1):
    found_before = export(cfg)
    count_before = count_samples(found_before, counter1._name)

    period = 0.2
    sleeps = 4
    sleep_sec = 0.25
    samples_expected = math.ceil((sleeps * sleep_sec) / period)  # + graceful one
    assert samples_expected > 0

    @ppc.influx_http_thread(cfg.vm_write_url, period=period)
    def _test():
        for _ in range(sleeps):
            counter1.inc()
            time.sleep(sleep_sec)
        return 1 / 0   # testing graceful stop

    with pytest.raises(ZeroDivisionError):
        _test()

    time.sleep(3.0)  # let them sync

    found_after = export(cfg)
    count_after = count_samples(found_after, counter1._name)

    for k in count_after.keys():
        assert samples_expected == count_after[k] - count_before[k]


@pytest.mark.asyncio
async def test_vic_influx_http_async(cfg, counter1):
    found_before = export(cfg)
    count_before = count_samples(found_before, counter1._name)

    period = 0.5
    sleeps = 3
    sleep_sec = 0.33
    samples_expected = math.ceil((sleeps * sleep_sec) / period)  # + graceful one
    assert samples_expected > 0

    async def _test():
        for _ in range(sleeps):
            counter1.inc()
            await asyncio.sleep(sleep_sec)
        return 1 / 0   # testing graceful stop

    with pytest.raises(ZeroDivisionError):
        async with ppc.influx_http_async(cfg.vm_write_url, period=period):
            await _test()

    await asyncio.sleep(3.0)  # let them sync

    found_after = export(cfg)
    count_after = count_samples(found_after, counter1._name)

    for k in count_after.keys():
        assert samples_expected == count_after[k] - count_before[k]


def test_vic_influx_udp_stream(cfg, counter1):
    found_before = export(cfg)
    count_before = count_samples(found_before, counter1._name)

    sleeps = 9
    sleep_sec = 0.1
    samples_expected = sleeps
    assert samples_expected > 0

    @ppc.influx_udp_stream(cfg.vm_host, cfg.vm_influx_port)
    def _test():
        for _ in range(sleeps):
            counter1.inc()
            time.sleep(sleep_sec)
        return 1 / 0

    with pytest.raises(ZeroDivisionError):
        _test()

    time.sleep(3.0)  # let them sync

    found_after = export(cfg)
    count_after = count_samples(found_after, counter1._name)

    for k in count_after.keys():
        assert samples_expected == count_after[k] - count_before[k]


@pytest.mark.asyncio
async def test_vic_influx_udp_aiostream(cfg, counter1):
    found_before = export(cfg)
    count_before = count_samples(found_before, counter1._name)

    sleeps = 9
    sleep_sec = 0.1
    samples_expected = sleeps
    assert samples_expected > 0

    async def _test():
        for _ in range(sleeps):
            counter1.inc()
            await asyncio.sleep(sleep_sec)

    async with ppc.influx_udp_aiostream(cfg.vm_host, cfg.vm_influx_port):
        await _test()

    await asyncio.sleep(3.0)  # let them sync

    found_after = export(cfg)
    count_after = count_samples(found_after, counter1._name)

    for k in count_after.keys():
        assert samples_expected == count_after[k] - count_before[k]


def test_vic_openmetrics_http_thread(cfg, counter1):
    found_before = export(cfg)
    count_before = count_samples(found_before, counter1._name)

    period = 0.2
    sleeps = 4
    sleep_sec = 0.25
    samples_expected = math.ceil((sleeps * sleep_sec) / period)  # + graceful one
    assert samples_expected > 0

    @ppc.openmetrics_http_thread(cfg.vm_import_url, period=period)
    def _test():
        for _ in range(sleeps):
            counter1.inc()
            time.sleep(sleep_sec)
        return 1 / 0   # testing graceful stop

    with pytest.raises(ZeroDivisionError):
        _test()

    time.sleep(3.0)  # let them sync

    found_after = export(cfg)
    count_after = count_samples(found_after, counter1._name)

    for k in count_after.keys():
        assert samples_expected == count_after[k] - count_before[k]


@pytest.mark.asyncio
async def test_vic_openmetrics_http_async(cfg, counter1):
    found_before = export(cfg)
    count_before = count_samples(found_before, counter1._name)

    period = 0.5
    sleeps = 3
    sleep_sec = 0.33
    samples_expected = math.ceil((sleeps * sleep_sec) / period)  # + graceful one
    assert samples_expected > 0

    async def _test():
        for _ in range(sleeps):
            counter1.inc()
            await asyncio.sleep(sleep_sec)
        return 1 / 0   # testing graceful stop

    with pytest.raises(ZeroDivisionError):
        async with ppc.openmetrics_http_async(cfg.vm_import_url, period=period):
            await _test()

    await asyncio.sleep(3.0)  # let them sync

    found_after = export(cfg)
    count_after = count_samples(found_after, counter1._name)

    for k in count_after.keys():
        assert samples_expected == count_after[k] - count_before[k]
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
    samples_expected = math.ceil(sleeps / period)  # + graceful one

    @ppc.influx_udp_thread(cfg.vm_host, cfg.vm_influx_port, period=period)
    def _test():
        for _ in range(sleeps):
            counter1.inc()
            time.sleep(sleep_sec)
        return 1 / 0   # testing graceful stop

    with pytest.raises(ZeroDivisionError):
        _test()

    time.sleep(2.0)  # let them sync

    found_after = export(cfg)
    count_after = count_samples(found_after, counter1._name)

    for k in count_after.keys():
        assert samples_expected == count_after[k] - count_before[k]


@pytest.mark.asyncio
async def test_vic_influx_udp_async(cfg, counter1):

    found_before = export(cfg)
    count_before = count_samples(found_before, counter1._name)

    period = 0.4
    sleeps = 2
    sleep_sec = 1.0
    samples_expected = math.ceil(sleeps / period)  # + graceful one

    @ppc.influx_udp_async(cfg.vm_host, cfg.vm_influx_port, period=period)
    async def _test():
        for _ in range(sleeps):
            counter1.inc()
            await asyncio.sleep(sleep_sec)
        return 1 / 0   # testing graceful stop

    with pytest.raises(ZeroDivisionError):
        await _test()

    await asyncio.sleep(2.0)  # let them sync

    found_after = export(cfg)
    count_after = count_samples(found_after, counter1._name)

    for k in count_after.keys():
        assert samples_expected == count_after[k] - count_before[k]

import pytest

import prometheus_push_client as ppc

from testutils import make_metric_fixture, collect_metrics, collect_formatter


@pytest.fixture
def hist1(request):
    return make_metric_fixture(request, ppc.Histogram(
        name="test_sub",
        unit="celsius",
        buckets=[-10, 0, 10, 20, float("inf")],
        labelnames=["l1", "l2"],
    ))


def test_openmetrics_format(hist1):

    hist1.labels(l1="Moscow", l2="today").observe(5)  # ((
    hist1.labels(l1=r"a\b", l2='purpose: "escape test"').observe(25)

    native_result = collect_metrics(hist1._name)
    fmt_result = collect_formatter(ppc.OpenMetricsFormat, hist1._name)

    assert native_result == fmt_result
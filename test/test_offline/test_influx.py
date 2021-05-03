import pytest

import prometheus_push_client as ppc

from testutils import make_metric_fixture, collect_formatter


NS = "test_offline"
SUB = "influx"


@pytest.fixture
def sum1(request):
    return make_metric_fixture(
        request,
        ppc.Summary(
            name="s1",
            namespace=NS,
            subsystem=SUB,
            labelnames=["l1", "l2"]
        )
    )


@pytest.fixture
def counter1(request):
    return make_metric_fixture(
        request,
        ppc.Counter(name="c1", namespace=NS, subsystem=SUB)
    )


@pytest.fixture
def histogram1(request):
    return make_metric_fixture(
        request,
        ppc.Histogram(
            name="h1",
            namespace=NS,
            subsystem=SUB,
            buckets=[1, 2, float("inf")],
            labelnames=["l1"],
        )
    )


@pytest.fixture
def influx_format_expected():
    return (""
"""
test_offline_influx_s1,l1=1,l2=2 count=2.0
test_offline_influx_s1,l1=1,l2=2 sum=10.0
test_offline_influx_s1,l1=10,l2=20 count=1.0
test_offline_influx_s1,l1=10,l2=20 sum=10.0
test_offline_influx_c1 total=10.0
test_offline_influx_h1,l1=1,le=1.0 bucket=1.0
test_offline_influx_h1,l1=1,le=2.0 bucket=2.0
test_offline_influx_h1,l1=1,le=+Inf bucket=3.0
test_offline_influx_h1,l1=1 count=3.0
test_offline_influx_h1,l1=1 sum=4.5
""").strip()


def test_influx_formatter(sum1, counter1, histogram1, influx_format_expected):
    sum1.labels(1, 2).observe(5)
    sum1.labels(l1=1, l2=2).observe(5)
    sum1.labels(l1=10, l2=20).observe(10)

    counter1.inc(10)

    histogram1.labels(l1=1).observe(0.5)
    histogram1.labels(l1=1).observe(1.5)
    histogram1.labels(l1=1).observe(2.5)

    data = collect_formatter(ppc.InfluxFormat)
    assert data == influx_format_expected


@pytest.fixture
def invalid_gauge(request):
    return make_metric_fixture(request, ppc.Gauge("justgauge"))


@pytest.fixture
def valid_gauge(request):
    return make_metric_fixture(request, ppc.Gauge("just_gauge"))


def test_influx_metric_name_invalid(invalid_gauge):
    with pytest.raises(ValueError):
        fmt = ppc.InfluxFormat()


def test_influx_metric_name_valid(valid_gauge):
    fmt = ppc.InfluxFormat()

    valid_gauge.inc(10)
    valid_gauge.inc(-5)

    data = fmt.generate_latest().decode()
    assert data == "just gauge=5.0"
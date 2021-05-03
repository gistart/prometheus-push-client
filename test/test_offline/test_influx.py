import pytest

import prometheus_push_client as ppc

from testutils import make_metric_fixture, collect_metrics


NS = "test_offline"
SUB = "influx"


@pytest.fixture
def sum1(request):
    return make_metric_fixture(
        request,
        ppc.Summary(name="s1", namespace=NS, subsystem=SUB)
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
        ppc.Histogram(name="h1", namespace=NS, subsystem=SUB, buckets=[1,2,float("inf")])
    )



def test_influx_formatter(sum1, counter1, histogram1):
    pass


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
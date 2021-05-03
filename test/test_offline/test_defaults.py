import pytest
import prometheus_push_client as ppc

from testutils import make_metric_fixture, collect_metrics

NS = "test_offline"
SUB = "defaults"


_cnt1 = ppc.Counter(
    name="c1",
    namespace=NS,
    subsystem=SUB,
    labelnames=["host", "l1", "l2"],
    default_labelvalues={
        "host": "localhost",
        "l1": 0,
    }
)

@pytest.fixture
def counter1(request):
    return make_metric_fixture(request, _cnt1)


@pytest.fixture
def test_defaults_expected():
    return \
"""
test_offline_defaults_c1_total{host="localhost",l1="0",l2="2"} 2.0
test_offline_defaults_c1_total{host="localhost",l1="1",l2="2"} 2.0
test_offline_defaults_c1_total{host="H",l1="1",l2="2"} 2.0
""".strip()


def test_default_labelvalues_usage(counter1, test_defaults_expected):
    # pairs of equivalent actions:

    counter1.labels(l2=2).inc()
    counter1.labels(2).inc()

    counter1.labels(l1=1, l2=2).inc()
    counter1.labels(1, 2).inc()

    counter1.labels(host="H", l1=1, l2=2).inc()
    counter1.labels("H", 1, 2).inc()

    res = collect_metrics(counter1._name)
    assert res == test_defaults_expected
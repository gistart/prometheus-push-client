[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/gistart/prometheus-push-client/test-all)](https://github.com/gistart/prometheus-push-client/actions)
[![Codecov](https://img.shields.io/codecov/c/github/gistart/prometheus-push-client)](https://codecov.io/gh/gistart/prometheus-push-client)

# prometheus-push-client

Push metrics from your regular and/or long-running jobs into existing Prometheus/VictoriaMetrics monitoring system.

:no-entry: not tested in real environment yet!

Currently supports pushes directly into VictoriaMetrics via UDP and HTTP using InfluxDB line protocol as [described here](https://docs.victoriametrics.com/Single-server-VictoriaMetrics.html?highlight=telegraf#how-to-send-data-from-influxdb-compatible-agents-such-as-telegraf), and into StatsD/statsd-exporter in StatsD format via UDP ([not ideal](https://github.com/prometheus/statsd_exporter#with-statsd)).

## Default labelvalues

With regular prometheus_client we can define defaults for either none or all our labels with `labelvalues`, but that's not enough.

We probably want to define some defaults, like `hostname`, or more importantly, **if we use VictoriaMetrics cluster** we need to push label `VictoriaMetrics_AccountID=<int>` (usually 1) or else our metrics will be ignored!

Following example shows how to use defaults, and how to override them if necessary.

```python
counter1 = ppc.Counter(
    name="c1",
    labelnames=["VictoriaMetrics_AccountID", "host", "event_type"],
    default_labelvalues={
        "VictoriaMetrics_AccountID": 1,
        "host": socket.gethostname(),
    }
)


# regular usage
counter1.labels(event_type="login").inc()

# overriding defaults
counter1.labels(host="non-default", event_type="login").inc()
# same effect as above: defaults are applied in `labelvalues`
# order for "missing" labels in the beginning
counter1.labels("non-default", "login").inc()
```

Metrics with no labels are initialized at creation time. This can have unpleasant side-effect: if we initialize lots of metrics not used in currently running job, background clients will have to push their non-changing values in every synchronization session.

To avoid that we'll have to properly isolate each task's metrics, which can be impossible or rather tricky, or we can create metrics with default, non-changing labels (like `hostname`). Such metrics will initialize on fisrt use (inc), and we'll be pusing only metrics we actually used!


## Background clients

Background clients spawn synchronization jobs "in background" (meaning in thread or asyncio task) to periodially send all metrics from `ppc.PUSH_REGISTRY` to the destination.

:warning: background clients will attempt to stop gracefully, syncronizing registry "for the last time" after our job exits or crashes. This _may_ mess up aggregation with sampling, I'm not sure yet.

Best way to use them -- via decorators. These clients are intended to be used with long running, but finite tasks, that could be spawned anywhere, therefor not easily accessible by the scraper. If that's not the case -- just use "passive mode" w/ the scaper)

``` python
def influx_udp_async(host, port, period=15.0):
def influx_udp_thread(host, port, period=15.0):
def influx_http_async(url, period=15.0):
def influx_http_thread(url, period=15.0):
def statsd_udp_async(host, port, period=15.0):
def statsd_udp_thread(host, port, period=15.0):
```

Usage example:
```python
import priometheus_push_client as ppc


req_hist = ppc.Histogram(
    name="external_requests",
    namespace="acme"
    subsystem="job123",
    unit="seconds",
    labelnames=["service"]
)



@ppc.influx_udp_async("victoria.acme.inc.net", 9876, period=15)
async def main(urls):
    # the job ...
    req_hist.labels(gethostname(url)).observe(response.elapsed)
    # ...
```
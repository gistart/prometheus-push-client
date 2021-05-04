from collections import defaultdict

from prometheus_push_client.formats.base import BaseFormat


class StatsdFormat(BaseFormat):

    """
    As described at:
    https://sysdig.com/blog/monitoring-statsd-metrics/

    No "realtime" types supported yet.
    """
    # TODO: support statsd native "sets", "timers" and "histograms" in FG mode

    FMT_DATAPOINT = "{measurement}{tag_set}:{value}|{dtype}"  # influx-style tags

    DTYPES = {
        "gauge": defaultdict(lambda: "g"),
        "counter": {
            "total": "c",
            "created": "g",
        },
        "summary": {
            "sum": "c",
            "count": "c",
            "created": "g",
        },
        "histogram": {
            "bucket": "c",
            "sum": "c",
            "count": "c",
            "created": "g",
        }

        # TODO: info, enum
    }


    def format_sample(self, sample, metric):
        # TODO: gauges reset?

        measurement_name = sample.name

        chunks = measurement_name.rsplit("_", 1)
        suffix = chunks[-1] if len(chunks) > 1 else None

        # dtype = self.DTYPES[metric.type][suffix]
        dtype = "g"  # TODO: omfg! everything behaves like gauge
        value = sample.value

        tag_set = ""
        if sample.labels:
            tags = ["", *(f"{k}={v}" for k, v in sample.labels.items())]
            tag_set = ",".join(tags)

        return self.FMT_DATAPOINT.format(
            measurement=measurement_name,
            tag_set=tag_set,
            value=value,
            dtype=dtype,
        )

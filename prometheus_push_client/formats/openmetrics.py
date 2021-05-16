from prometheus_push_client.formats.base import BaseFormat


class OpenMetricsFormat(BaseFormat):
    """
    As described at:
    https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md
    """

    FMT_DATATYPE = "# TYPE %(measurement)s %(dtype)s"
    FMT_DATAPOINT = "%(measurement)s%(tag_set)s %(value)s%(timestamp)s"

    ESCAPING = str.maketrans({
        '"': r'\"',
        '\\': r'\\',
        '\n': r'\n',
    })


    def format_header(self, metric):  # pragma: no cover
        # as in generate_latest implemented at:
        # https://github.com/prometheus/client_python/blob/master/prometheus_client/exposition.py

        mname, mtype = metric.name, metric.type
        if metric.type == "counter":
            mname = f"{mname}_total"
        elif metric.type in ("info", "stateset"):
            mtype = "gauge"
        elif metric.type == "gaugehistogram":
            mtype = "histogram"

        yield self.FMT_DATATYPE % dict(measurement=mname, dtype=mtype)
        yield self.FMT_DATATYPE % dict(
            measurement=f"{metric.name}_created",
            dtype="gauge"
        )

    def format_sample(self, sample, _):
        tag_set = ""
        if sample.labels:
            tags = (f'{k}="{v.translate(self.ESCAPING)}"' for k, v in sample.labels.items())
            tag_set = "{%s}" % ",".join(tags)

        ts = ""
        if sample.timestamp:  # pragma: no cover
            ts = " %s" % sample.timestamp

        return self.FMT_DATAPOINT % dict(
            measurement=sample.name,
            tag_set=tag_set,
            value=sample.value,
            timestamp=ts,
        )
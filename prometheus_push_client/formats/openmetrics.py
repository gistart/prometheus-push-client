import prometheus_client as pc

from prometheus_push_client.formats.base import BaseFormat


class OpenMetricsFormat(BaseFormat):
    """
    As described at:
    https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md
    """

    FMT_DATAPOINT = "%(measurement)s%(tag_set)s %(value)s%(timestamp)s"

    ESCAPING = str.maketrans({
        '"': r'\"',
        '\\': r'\\',
        '\n': r'\n',
    })


    def format_sample(self, sample, metric):
        tag_set = ""
        if sample.labels:
            tags = (f'{k}="{v.translate(self.ESCAPING)}"' for k, v in sample.labels.items())
            tag_set = "{%s}" % ",".join(tags)

        ts = ""
        if sample.timestamp:  # pragma: no cover
            ts = " %s" % sample.timestamp

        # TODO: TYPE string?
        return self.FMT_DATAPOINT % dict(
            measurement=sample.name,
            tag_set=tag_set,
            value=sample.value,
            timestamp=ts,
        )

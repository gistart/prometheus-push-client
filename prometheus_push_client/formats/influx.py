from prometheus_push_client.formats.base import BaseFormat


class InfluxFormat(BaseFormat):
    """
    As descibed at:
    https://docs.influxdata.com/influxdb/v1.8/write_protocols/line_protocol_tutorial/
    """

    FMT_SAMPLE = "{sample_name}{tag_set} {measurement_name}={value}{timestamp}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_metric_names(self.registry)

    def validate_metric_names(self, registry):
        names_not_supported = []
        for metric_name in self.registry._names_to_collectors.keys():
            if "_" not in metric_name:
                names_not_supported.append(metric_name)

        if names_not_supported:
            raise ValueError(
                "Following metrics can't be exported to Influx. Add `namespace`, "
                "`subsystem`, `unit`, or just come up with 'two_words' name: "
                f"{names_not_supported}"
            )

    def format_sample(self, sample, *_):
        sample_name, measurement_name = sample.name.rsplit("_", 1)

        tag_set = ""
        if sample.labels:
            tags = ["", *(f"{k}={v}" for k, v in sample.labels.items())]
            tag_set = ",".join(tags)

        ts = ""
        if sample.timestamp:  # pragma: no cover
            ts = f" {int(sample.timestamp * 1e9)}"  # to nanoseconds

        return self.FMT_SAMPLE.format(
            sample_name=sample_name,
            tag_set=tag_set,
            measurement_name=measurement_name,
            value=sample.value,
            timestamp=ts,
        )
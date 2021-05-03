from prometheus_push_client.formats.base import BaseFormat


class GraphiteFormat(BaseFormat):

    FMT_DATAPOINT = "{measurement}:{value}|{dtype}"  # no sampling?

    DTYPES = {
        "counter": "c",
        "gauge": "g",
        "info": "s",
        "enum": "s", # TODO?
        # histogram and summary are always counters?
        "histogram": "c",
        "summary": "c",
    }

    def format_sample(self, sample, metric):
        measurement_name = sample.name
        if sample.labels:
            tags = " ".join(f"{k}={v}" for k,v in sample.labels.items())
            measurement_name = f"{measurement_name},{tags}"

        dtype = self.DTYPES.get(metric.type)
        value = sample.value

        # https://prometheus.io/docs/practices/naming/#base-units
        if metric.type == "counter":  # TODO: other types
            if metric.unit == "seconds":
                dtype = "ms"
                value *= 1000

        if dtype is None:
            raise NotImplementedError(f"cant convert type:{metric.type} unit:{metric.unit}")

        if isinstance(value, float):
            value = int(round(value))  # TODO

        return self.FMT_DATAPOINT.format(
            measurement=measurement_name,
            value=value,
            dtype=dtype,
        )

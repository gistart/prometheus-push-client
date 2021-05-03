import prometheus_client as pc

from prometheus_push_client.formats.base import BaseFormat


class PrometheusFormat(BaseFormat):
    # e.g. pushgateway

    def iter_samples(self):
        data = pc.generate_latest(self.registry)
        for line in data.strip().split(b"\n"):
            if line.startswith(b"#"):
                continue
            yield line

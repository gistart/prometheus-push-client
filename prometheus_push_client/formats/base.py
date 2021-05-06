import time

from prometheus_push_client.registry import PUSH_REGISTRY


class BaseFormat:
    def __init__(self, registry=PUSH_REGISTRY):
        self.registry = registry

    def generate_latest(self):
        samples = self.iter_samples()
        return b"\n".join(samples)

    def iter_samples(self):
        for metric in self.registry.collect():
            for line in self.format_metrics(metric):
                yield line

    def format_metrics(self, *metrics):
        for metric in metrics:
            for sample in metric.samples:
                line = self.format_sample(sample, metric)
                if isinstance(line, str):
                    line = line.encode("utf-8")
                yield line

    def format_sample(self, metric, sample):
        raise NotImplementedError()
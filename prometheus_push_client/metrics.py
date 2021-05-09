import prometheus_client as pc

from prometheus_push_client.registry import PUSH_REGISTRY


class _PushMixin:
    def __init__(self, name, documentation="", default_labelvalues=None, **kwargs):
        kwargs["registry"] = kwargs.get("registry", PUSH_REGISTRY)
        self._default_labelvalues = default_labelvalues or {}
        super().__init__(name, documentation, **kwargs)

    def labels(self, *labelvalues, **labelkwargs):
        if labelkwargs:
            if len(labelkwargs) < len(self._labelnames):
                labelkwargs = {**self._default_labelvalues, **labelkwargs}

        elif len(labelvalues) < len(self._labelnames):
            from_defaults = len(self._labelnames) - len(labelvalues)
            defaults = (
                self._default_labelvalues[l]
                for l in self._labelnames[:from_defaults]
            )
            labelvalues = (*defaults, *labelvalues)

        return super().labels(*labelvalues, **labelkwargs)


class Counter(_PushMixin, pc.Counter): pass
class Gauge(_PushMixin, pc.Gauge): pass
class Summary(_PushMixin, pc.Summary): pass
class Histogram(_PushMixin, pc.Histogram): pass

# TODO: Info, Enum ?

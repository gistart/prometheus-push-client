import logging
from types import MethodType


log = logging.getLogger("prometheus.streaming")

METRIC_METHODS = ("inc", "dec", "set", "observe")


class BaseStreamingClient:
    def __init__(self, format, transport):
        self.format = format
        self.transport = transport

    def _monkey_patch_all(self):
        registry = self.format.registry
        with registry._lock:
            patch_registry(registry, self.format, self.transport)
            for collector in registry._collector_to_names.keys():
                patch_collector(collector, self.format, self.transport)

    def _restore_all(self):
        registry = self.format.registry
        with registry._lock:
            restore_registry(registry)
            for collector in registry._collector_to_names.keys():
                restore_collector(collector)


class SyncStreamingClient(BaseStreamingClient):
    def start(self):
        self._monkey_patch_all()
        self.transport.start()

    def stop(self):
        self._restore_all()
        self.transport.stop()


class AsyncStreamingClient(BaseStreamingClient):
    async def start(self):
        self._monkey_patch_all()
        await self.transport.start()

    async def stop(self):
        self._restore_all()
        await self.transport.stop()


def push_all(collector, format, transport):
    try:
        metrics = collector.collect()
        data_gen = format.format_metrics(*metrics)
        transport.push_all_sync(data_gen)
    except Exception:
        log.error("push crashed", exc_info=True)


#
## Utils for monkey-patching
#


def patch_registry(registry, format, transport):
    register_orig = registry.register

    def register_new(self, collector, *args, **kwargs):
        patch_collector(collector, format, transport)
        register_orig(collector, *args, **kwargs)

    setattr(registry, "register", MethodType(register_new, registry))


def patch_collector(collector, format, transport, parent=None):
    # own methods
    for method_name in METRIC_METHODS:
        if not hasattr(collector, method_name):
            continue
        patch_collector_method(collector, format, transport, method_name, parent)

    # child _metrics
    if hasattr(collector, "_metrics"):
        with collector._lock:
            patch_collector_submetrics(collector, format, transport)


def patch_collector_method(collector, format, transport, method_name, parent=None):
    method_orig = getattr(collector, method_name)

    def method_new(self, *args, **kwargs):
        method_orig(*args, **kwargs)

        push_from = self if parent is None else parent
        push_all(push_from, format, transport)

    setattr(collector, method_name, MethodType(method_new, collector))


def patch_collector_submetrics(collector, format, transport):
    new_container = SelfPatchingMetrics(collector, format, transport)

    for orig_key in list(collector._metrics.keys()):
        orig_collector = collector._metrics.pop(orig_key)
        new_container[orig_key] = orig_collector

    collector._metrics = new_container


class SelfPatchingMetrics(dict):
    def __init__(self, parent, format, transport):
        self.parent = parent
        self.format = format
        self.transport = transport
        dict.__init__(self)

    def __setitem__(self, key, submetric):
        patch_collector(submetric, self.format, self.transport, self.parent)
        dict.__setitem__(self, key, submetric)


def restore_registry(registry):
    setattr(
        registry,
        "register",
        MethodType(
            registry.__class__.register,
            registry
        )
    )


def restore_collector(collector):
    for method_name in METRIC_METHODS:
        if not hasattr(collector, method_name):
            continue

        setattr(
            collector,
            method_name,
            MethodType(
                getattr(collector.__class__, method_name),
                collector,
            )
        )

    if hasattr(collector, "_metrics"):
        with collector._lock:
            collector._metrics = {**collector._metrics}
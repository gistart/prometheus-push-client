import prometheus_client as pc


PUSH_REGISTRY = pc.CollectorRegistry(auto_describe=False, target_info=None)


def transfer_metrics(src_registry, dst_registry):  # pragma: no cover
    """
    From ppc.PUSH_REGISTRY to pc.REGISTRY or vice versa
    """

    with src_registry._lock:
        with dst_registry._lock:
            for collector in src_registry._collector_to_names:
                src_registry.unregister(collector)
                dst_registry.register(collector)
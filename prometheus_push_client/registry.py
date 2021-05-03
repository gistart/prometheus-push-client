import prometheus_client as pc


class PushRegistry(pc.CollectorRegistry):
    pass


PUSH_REGISTRY = PushRegistry()

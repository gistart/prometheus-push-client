import prometheus_client as pc
import prometheus_push_client as ppc


def make_metric_fixture(request, metric):
    if metric._name not in ppc.PUSH_REGISTRY._names_to_collectors:
        ppc.PUSH_REGISTRY.register(metric)

    def unregister():
        metric._metric_init()
        if metric._name in ppc.PUSH_REGISTRY._names_to_collectors:
            ppc.PUSH_REGISTRY.unregister(metric)
    request.addfinalizer(unregister)

    return metric


def collect_metrics(*metric_names):
    all_data = pc.generate_latest(ppc.PUSH_REGISTRY).decode()

    def only_interesting(line):
        return (
            line and
            any(
                line.startswith(m) and not line.startswith(f"{m}_created")
                for m in metric_names
            )
        )

    interesting_lines = filter(only_interesting, all_data.split("\n"))
    return "\n".join(interesting_lines)
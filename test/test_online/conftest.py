import os
import pytest


@pytest.fixture
def cfg():

    class Cfg:
        vm_host = os.getenv("VM_HOST", "localhost")
        vm_api_port = os.getenv("VM_API_PORT", "8428")
        vm_influx_port = os.getenv("VM_INFLUX_PORT", "8491")

        statsd_host = os.getenv("STATSD_HOST", "localhost")
        statsd_api_port = os.getenv("STATSD_API_PORT", "9102")
        statsd_udp_port = os.getenv("STATSD_UDP_PORT", "9125")

        pushgw_host = os.getenv("PUSHGW_HOST", "localhost")
        pushgw_port = os.getenv("PUSHGW_PORT", "9091")

        vm_ping_url = f"http://{vm_host}:{vm_api_port}/health"
        vm_write_url = f"http://{vm_host}:{vm_api_port}/write"
        vm_export_url = f"http://{vm_host}:{vm_api_port}/api/v1/export"
        vm_import_url = f"http://{vm_host}:{vm_api_port}/api/v1/import/prometheus"

        statsd_url = f"http://{statsd_host}:{statsd_api_port}/metrics"

        pushgw_url = f"http://{pushgw_host}:{pushgw_port}/metrics"

    return Cfg()
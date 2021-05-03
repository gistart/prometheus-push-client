import os
import pytest


@pytest.fixture
def cfg():

    class Cfg:
        vm_host = os.getenv("VM_HOST", "localhost")
        vm_api_port = os.getenv("VM_API_PORT", "8428")
        vm_influx_port = os.getenv("VM_INFLUX_PORT", "8491")
        vm_graphite_port = os.getenv("VM_GRAPHITE_PORT", "8492")

        vm_ping_url = f"http://{vm_host}:{vm_api_port}/health"
        vm_write_url = f"http://{vm_host}:{vm_api_port}/write"
        vm_export_url = f"http://{vm_host}:{vm_api_port}/api/v1/export"

    return Cfg()
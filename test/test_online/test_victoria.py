import pytest
import requests


def test_ping(cfg):
    response = requests.get(cfg.vm_ping_url)
    content = response.text

    assert response.status_code == 200, content
    assert content == "OK", content
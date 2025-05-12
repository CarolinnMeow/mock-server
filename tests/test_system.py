# tests/test_system.py
import pytest

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()["status"] == "OK"

def test_metrics(client):
    response = client.get('/metrics')
    assert response.status_code == 200
    assert "accounts" in response.get_json()

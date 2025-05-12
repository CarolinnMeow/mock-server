# tests/test_vrp.py
import pytest

def test_create_vrp(client):
    data = {
        "max_amount": 5000,
        "frequency": "MONTHLY",
        "valid_until": "2026-01-01",
        "recipient_account": "RU0012345678"
    }
    response = client.post('/vrp-v1.3.1/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["max_amount"] == 5000
    assert resp_json["frequency"] == "MONTHLY"

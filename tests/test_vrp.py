# tests/test_vrp.py

import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_vrp(client):
    data = {
        "max_amount": 5000,
        "frequency": "MONTHLY",
        "valid_until": "2026-01-01",
        "recipient_account": "acc-123"
    }
    response = client.post('/vrp-v1.3.1/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["max_amount"] == 5000
    assert resp_json["frequency"] == "MONTHLY"

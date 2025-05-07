# tests/test_consents.py

import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_physical_consent(client):
    data = {
        "tpp_id": "tpp1",
        "permissions": ["read", "write"]
    }
    response = client.post('/consent-pe-v2.0.0/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["type"] == "physical_entity"
    assert resp_json["status"] == "ACTIVE"
    assert resp_json["tpp_id"] == "tpp1"
    assert "permissions" in resp_json

def test_create_legal_consent(client):
    data = {
        "tpp_id": "tpp2",
        "permissions": ["read"]
    }
    response = client.post('/consent-le-v2.0.0/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["type"] == "legal_entity"
    assert resp_json["tpp_id"] == "tpp2"

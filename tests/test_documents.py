# tests/test_documents.py

import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_bank_doc(client):
    data = {
        "type": "STATEMENT",
        "content": "dGVzdA==",
        "signature": "sig123"
    }
    response = client.post('/bank-doc-v1.0.1/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["type"] == "STATEMENT"
    assert resp_json["signature"] == "sig123"

def test_create_insurance_doc(client):
    data = {
        "type": "POLICY",
        "content": "dGVzdA==",
        "policy_number": "P12345",
        "valid_until": "2025-12-31"
    }
    response = client.post('/insurance-doc-v1.0.1/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["type"] == "POLICY"
    assert resp_json["policy_number"] == "P12345"


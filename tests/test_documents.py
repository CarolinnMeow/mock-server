# tests/test_documents.py
import pytest



def test_create_bank_doc(client):
    resp = client.get('/accounts-v1.3.3/')
    accounts = resp.get_json()
    assert accounts
    account_id = accounts[0]["id"]

    data = {
        "type": "STATEMENT",
        "content": "dGVzdA==",
        "signature": "sig123",
        "account_id": account_id
    }
    response = client.post('/bank-doc-v1.0.1/', json=data)
    assert response.status_code == 201


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


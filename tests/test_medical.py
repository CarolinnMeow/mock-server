# tests/test_medical.py
import pytest


def test_create_medical_insured(client):
    data = {
        "name": "Иван Иванов",
        "policy_number": "POL123456",
        "birth_date": "1990-01-01"
    }
    response = client.post('/medical-insured-person-v3.0.3/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["name"] == "Иван Иванов"
    assert resp_json["policy_number"] == "POL123456"

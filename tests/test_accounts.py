# tests/test_accounts.py
import pytest


def test_get_physical_accounts(client):
    """
    Проверка получения списка счетов физических лиц.
    """
    response = client.get('/accounts-v1.3.3/')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

    if data:
        acc = data[0]
        assert "id" in acc
        assert "balance" in acc
        assert "currency" in acc
        assert "owner" in acc

def test_create_physical_account(client):
    """
    Проверка создания счета физического лица.
    """
    data = {
        "balance": 1000,
        "currency": "RUB",
        "owner": "Иван Иванов",
        "status": "active"
    }
    response = client.post('/accounts-v1.3.3/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["balance"] == 1000
    assert resp_json["currency"] == "RUB"
    assert resp_json["owner"] == "Иван Иванов"
    assert "id" in resp_json
    assert "status" in resp_json
    assert resp_json["status"] == "active"

def test_create_account_missing_owner(client):
    data = {
        "balance": 1000,
        "currency": "RUB",
        "status": "active"
    }
    response = client.post('/accounts-v1.3.3/', json=data)
    assert response.status_code == 400

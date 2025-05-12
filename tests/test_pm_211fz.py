import pytest



def test_create_pm_211fz(client):
    # Получить существующий account_id
    resp = client.get('/accounts-v1.3.3/')
    accounts = resp.get_json()
    assert accounts
    account_id = accounts[0]["id"]

    data = {
        "amount": 1000,
        "currency": "RUB",
        "recipient": "budget-acc-1",
        "purpose": "Оплата налогов",
        "budget_code": "18210102010011000110",
        "account_id": account_id
    }
    response = client.post('/pm-211fz-v1.3.1/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["status"] == "PENDING"
    assert resp_json["type"] == "pm_211fz"



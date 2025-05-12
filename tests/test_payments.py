import pytest

def test_create_payment(client):
    # 1. Получить список счетов
    resp = client.get('/accounts-v1.3.3/')
    accounts = resp.get_json()
    assert accounts, "Нет ни одного счета в тестовой базе!"
    account_id = accounts[0]["id"]  # Берём id первого счёта

    # 2. Использовать account_id при создании платежа
    data = {
        "amount": 100,
        "currency": "RUB",
        "recipient": "Иван",
        "account_id": account_id
    }
    response = client.post('/payments-v1.3.1/', json=data)
    assert response.status_code == 201
    payment = response.get_json()
    assert payment["account_id"] == account_id


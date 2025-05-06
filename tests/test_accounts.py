# tests/test_accounts.py
# Тесты для эндпоинтов работы со счетами.

import pytest
from app import create_app

@pytest.fixture
def client():
    """
    Фикстура для тестового клиента Flask.
    """
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_physical_accounts(client):
    """
    Проверка получения списка счетов физических лиц.
    """
    response = client.get('/accounts-v1.3.3/')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_create_physical_account(client):
    """
    Проверка создания счета физического лица.
    """
    data = {"balance": 1000, "currency": "RUB"}
    response = client.post('/accounts-v1.3.3/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["balance"] == 1000
    assert resp_json["currency"] == "RUB"

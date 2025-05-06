import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_payment(client):
    data = {"amount": 100, "currency": "RUB", "recipient": "Ivan"}
    response = client.post('/payments-v1.3.1/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["amount"] == 100
    assert resp_json["currency"] == "RUB"
    assert resp_json["recipient"] == "Ivan"

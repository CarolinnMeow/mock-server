import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_pm_211fz(client):
    data = {
        "amount": 1000,
        "currency": "RUB",
        "recipient": "budget-acc-1"
    }
    response = client.post('/pm-211fz-v1.3.1/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["status"] == "PROCESSING"
    assert resp_json["type"] == "pm_211fz"

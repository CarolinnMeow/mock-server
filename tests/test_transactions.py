# tests/test_transactions.py

import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_transactions(client):
    response = client.get('/transaction-history-v1.0.0/')
    assert response.status_code == 200
    assert "transactions" in response.get_json()

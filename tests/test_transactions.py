# tests/test_transactions.py
import pytest


def test_get_transactions(client):
    response = client.get('/transaction-history-v1.0.0/')
    assert response.status_code == 200
    assert "transactions" in response.get_json()

# tests/test_product_agreements.py
import pytest


def test_create_product_agreement(client):
    data = {
        "product_type": "LOAN",
        "terms": {"rate": 0.15, "duration": 12}
    }
    response = client.post('/product-agreement-consents-v1.0.1/', json=data)
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["product_type"] == "LOAN"

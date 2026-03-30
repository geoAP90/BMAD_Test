from fastapi.testclient import TestClient
from main import app
import json
from datetime import date

client = TestClient(app)

def test_create_payment():
    payment_data = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 100.0
    }
    response = client.post("/payments/", json=payment_data)
    assert response.status_code == 201
    assert response.json() == payment_data

def test_get_all_payments():
    payment_data = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 100.0
    }
    client.post("/payments/", json=payment_data)
    response = client.get("/payments/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0] == payment_data

def test_get_payment_by_id():
    payment_data = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 100.0
    }
    client.post("/payments/", json=payment_data)
    response = client.get("/payments/1")
    assert response.status_code == 200
    assert response.json() == payment_data

def test_update_payment():
    payment_data = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 100.0
    }
    client.post("/payments/", json=payment_data)
    updated_payment_data = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 150.0
    }
    response = client.put("/payments/1", json=updated_payment_data)
    assert response.status_code == 200
    assert response.json() == updated_payment_data

def test_delete_payment():
    payment_data = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 100.0
    }
    client.post("/payments/", json=payment_data)
    response = client.delete("/payments/1")
    assert response.status_code == 204

def test_get_non_existent_payment():
    response = client.get("/payments/1")
    assert response.status_code == 404

def test_update_non_existent_payment():
    payment_data = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 100.0
    }
    response = client.put("/payments/1", json=payment_data)
    assert response.status_code == 404

def test_delete_non_existent_payment():
    response = client.delete("/payments/1")
    assert response.status_code == 404
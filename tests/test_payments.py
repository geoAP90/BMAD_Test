from fastapi.testclient import TestClient
from main import app
import json
from models import Payment

client = TestClient(app)

def test_create_payment():
    payment = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 100.0
    }
    response = client.post("/payments/", json=payment)
    assert response.status_code == 201
    assert response.json() == payment

def test_get_all_payments():
    payment1 = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 100.0
    }
    payment2 = {
        "id": 2,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 200.0
    }
    client.post("/payments/", json=payment1)
    client.post("/payments/", json=payment2)
    response = client.get("/payments/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_payment_by_id():
    payment = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 100.0
    }
    client.post("/payments/", json=payment)
    response = client.get("/payments/1")
    assert response.status_code == 200
    assert response.json() == payment

def test_update_payment():
    payment = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 100.0
    }
    updated_payment = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 200.0
    }
    client.post("/payments/", json=payment)
    response = client.put("/payments/1", json=updated_payment)
    assert response.status_code == 200
    assert response.json() == updated_payment

def test_delete_payment():
    payment = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 100.0
    }
    client.post("/payments/", json=payment)
    response = client.delete("/payments/1")
    assert response.status_code == 204

def test_get_non_existent_payment():
    response = client.get("/payments/1")
    assert response.status_code == 404

def test_update_non_existent_payment():
    payment = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 100.0
    }
    response = client.put("/payments/1", json=payment)
    assert response.status_code == 404

def test_delete_non_existent_payment():
    response = client.delete("/payments/1")
    assert response.status_code == 404
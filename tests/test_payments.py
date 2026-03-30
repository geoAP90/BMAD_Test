from fastapi.testclient import TestClient
from main import app
import json
from datetime import date

client = TestClient(app)

def test_create_payment():
    payment = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 1000.0
    }
    claim = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2022-01-01",
        "claim_amount": 1000.0,
        "status": "pending"
    }
    policy = {
        "id": 1,
        "policy_number": "12345",
        "policy_holder": "John Doe",
        "policy_type": "Life Insurance",
        "start_date": "2022-01-01",
        "end_date": "2023-01-01"
    }
    client.post("/policies/", json=policy)
    client.post("/claims/", json=claim)
    response = client.post("/payments/", json=payment)
    assert response.status_code == 201
    assert response.json() == payment

def test_get_payments():
    payment1 = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 1000.0
    }
    payment2 = {
        "id": 2,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 2000.0
    }
    claim = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2022-01-01",
        "claim_amount": 1000.0,
        "status": "pending"
    }
    policy = {
        "id": 1,
        "policy_number": "12345",
        "policy_holder": "John Doe",
        "policy_type": "Life Insurance",
        "start_date": "2022-01-01",
        "end_date": "2023-01-01"
    }
    client.post("/policies/", json=policy)
    client.post("/claims/", json=claim)
    client.post("/payments/", json=payment1)
    client.post("/payments/", json=payment2)
    response = client.get("/payments/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_payment():
    payment = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 1000.0
    }
    claim = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2022-01-01",
        "claim_amount": 1000.0,
        "status": "pending"
    }
    policy = {
        "id": 1,
        "policy_number": "12345",
        "policy_holder": "John Doe",
        "policy_type": "Life Insurance",
        "start_date": "2022-01-01",
        "end_date": "2023-01-01"
    }
    client.post("/policies/", json=policy)
    client.post("/claims/", json=claim)
    client.post("/payments/", json=payment)
    response = client.get("/payments/1")
    assert response.status_code == 200
    assert response.json() == payment

def test_update_payment():
    payment = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 1000.0
    }
    updated_payment = {
        "id": 1,
        "claim_id": 1,
        "payment_date": "2022-01-01",
        "payment_amount": 2000.0
    }
    claim = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2022-01-01",
        "claim_amount": 1000.0,
        "status": "pending"
    }
    policy = {
        "id": 1,
        "policy_number": "12345",
        "policy_holder": "John Doe",
        "policy_type": "Life Insurance",
        "start_date": "2022-01
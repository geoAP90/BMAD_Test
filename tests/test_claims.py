from fastapi.testclient import TestClient
from main import app
import json
from datetime import date

client = TestClient(app)

def test_create_claim():
    claim = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2020-01-01",
        "claim_amount": 1000.0,
        "status": "pending"
    }
    response = client.post("/claims/", json=claim)
    assert response.status_code == 201
    assert response.json() == claim

def test_get_all_claims():
    claim1 = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2020-01-01",
        "claim_amount": 1000.0,
        "status": "pending"
    }
    claim2 = {
        "id": 2,
        "policy_id": 2,
        "claim_date": "2020-01-01",
        "claim_amount": 2000.0,
        "status": "pending"
    }
    client.post("/claims/", json=claim1)
    client.post("/claims/", json=claim2)
    response = client.get("/claims/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_claim_by_id():
    claim = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2020-01-01",
        "claim_amount": 1000.0,
        "status": "pending"
    }
    client.post("/claims/", json=claim)
    response = client.get("/claims/1")
    assert response.status_code == 200
    assert response.json() == claim

def test_update_claim():
    claim = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2020-01-01",
        "claim_amount": 1000.0,
        "status": "pending"
    }
    updated_claim = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2020-01-01",
        "claim_amount": 2000.0,
        "status": "approved"
    }
    client.post("/claims/", json=claim)
    response = client.put("/claims/1", json=updated_claim)
    assert response.status_code == 200
    assert response.json() == updated_claim

def test_delete_claim():
    claim = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2020-01-01",
        "claim_amount": 1000.0,
        "status": "pending"
    }
    client.post("/claims/", json=claim)
    response = client.delete("/claims/1")
    assert response.status_code == 204

def test_get_non_existent_claim():
    response = client.get("/claims/1")
    assert response.status_code == 404

def test_update_non_existent_claim():
    claim = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2020-01-01",
        "claim_amount": 1000.0,
        "status": "pending"
    }
    response = client.put("/claims/1", json=claim)
    assert response.status_code == 404

def test_delete_non_existent_claim():
    response = client.delete("/claims/1")
    assert response.status_code == 404
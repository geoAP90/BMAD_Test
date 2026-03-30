from fastapi.testclient import TestClient
from main import app
import json
from datetime import date

client = TestClient(app)

def test_create_claim():
    claim_data = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2022-01-01",
        "claim_amount": 100.0,
        "status": "pending"
    }
    response = client.post("/claims/", json=claim_data)
    assert response.status_code == 201
    assert response.json() == claim_data

def test_get_all_claims():
    claim_data = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2022-01-01",
        "claim_amount": 100.0,
        "status": "pending"
    }
    client.post("/claims/", json=claim_data)
    response = client.get("/claims/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0] == claim_data

def test_get_claim_by_id():
    claim_data = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2022-01-01",
        "claim_amount": 100.0,
        "status": "pending"
    }
    client.post("/claims/", json=claim_data)
    response = client.get("/claims/1")
    assert response.status_code == 200
    assert response.json() == claim_data

def test_update_claim():
    claim_data = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2022-01-01",
        "claim_amount": 100.0,
        "status": "pending"
    }
    client.post("/claims/", json=claim_data)
    updated_claim_data = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2022-01-01",
        "claim_amount": 150.0,
        "status": "approved"
    }
    response = client.put("/claims/1", json=updated_claim_data)
    assert response.status_code == 200
    assert response.json() == updated_claim_data

def test_delete_claim():
    claim_data = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2022-01-01",
        "claim_amount": 100.0,
        "status": "pending"
    }
    client.post("/claims/", json=claim_data)
    response = client.delete("/claims/1")
    assert response.status_code == 204

def test_get_non_existent_claim():
    response = client.get("/claims/1")
    assert response.status_code == 404

def test_update_non_existent_claim():
    claim_data = {
        "id": 1,
        "policy_id": 1,
        "claim_date": "2022-01-01",
        "claim_amount": 100.0,
        "status": "pending"
    }
    response = client.put("/claims/1", json=claim_data)
    assert response.status_code == 404

def test_delete_non_existent_claim():
    response = client.delete("/claims/1")
    assert response.status_code == 404
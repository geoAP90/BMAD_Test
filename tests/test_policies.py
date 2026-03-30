from fastapi.testclient import TestClient
from main import app
import json
from datetime import date

client = TestClient(app)

def test_create_policy():
    policy = {
        "id": 1,
        "policy_number": "12345",
        "policy_holder": "John Doe",
        "policy_type": "Life Insurance",
        "start_date": "2020-01-01",
        "end_date": "2021-01-01"
    }
    response = client.post("/policies/", json=policy)
    assert response.status_code == 201
    assert response.json() == policy

def test_get_all_policies():
    policy1 = {
        "id": 1,
        "policy_number": "12345",
        "policy_holder": "John Doe",
        "policy_type": "Life Insurance",
        "start_date": "2020-01-01",
        "end_date": "2021-01-01"
    }
    policy2 = {
        "id": 2,
        "policy_number": "67890",
        "policy_holder": "Jane Doe",
        "policy_type": "Health Insurance",
        "start_date": "2020-01-01",
        "end_date": "2021-01-01"
    }
    client.post("/policies/", json=policy1)
    client.post("/policies/", json=policy2)
    response = client.get("/policies/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_policy_by_id():
    policy = {
        "id": 1,
        "policy_number": "12345",
        "policy_holder": "John Doe",
        "policy_type": "Life Insurance",
        "start_date": "2020-01-01",
        "end_date": "2021-01-01"
    }
    client.post("/policies/", json=policy)
    response = client.get("/policies/1")
    assert response.status_code == 200
    assert response.json() == policy

def test_update_policy():
    policy = {
        "id": 1,
        "policy_number": "12345",
        "policy_holder": "John Doe",
        "policy_type": "Life Insurance",
        "start_date": "2020-01-01",
        "end_date": "2021-01-01"
    }
    updated_policy = {
        "id": 1,
        "policy_number": "67890",
        "policy_holder": "Jane Doe",
        "policy_type": "Health Insurance",
        "start_date": "2020-01-01",
        "end_date": "2021-01-01"
    }
    client.post("/policies/", json=policy)
    response = client.put("/policies/1", json=updated_policy)
    assert response.status_code == 200
    assert response.json() == updated_policy

def test_delete_policy():
    policy = {
        "id": 1,
        "policy_number": "12345",
        "policy_holder": "John Doe",
        "policy_type": "Life Insurance",
        "start_date": "2020-01-01",
        "end_date": "2021-01-01"
    }
    client.post("/policies/", json=policy)
    response = client.delete("/policies/1")
    assert response.status_code == 204

def test_get_non_existent_policy():
    response = client.get("/policies/1")
    assert response.status_code == 404

def test_update_non_existent_policy():
    policy = {
        "id": 1,
        "policy_number": "12345",
        "policy_holder": "John Doe",
        "policy_type": "Life Insurance",
        "start_date": "2020-01-01",
        "end_date": "2021-01-01"
    }
    response = client.put("/policies/1", json=policy)
    assert response.status_code == 404

def test_delete_non_existent_policy():
    response = client.delete("/policies/1")
    assert response.status_code == 404
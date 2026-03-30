from fastapi.testclient import TestClient
from main import app
import json
from datetime import date

client = TestClient(app)

def test_create_policy():
    policy_data = {
        "id": 1,
        "policy_number": "12345",
        "policyholder_name": "John Doe",
        "policy_start_date": "2022-01-01",
        "policy_end_date": "2023-01-01"
    }
    response = client.post("/policies/", json=policy_data)
    assert response.status_code == 201
    assert response.json() == policy_data

def test_get_all_policies():
    policy_data = {
        "id": 1,
        "policy_number": "12345",
        "policyholder_name": "John Doe",
        "policy_start_date": "2022-01-01",
        "policy_end_date": "2023-01-01"
    }
    client.post("/policies/", json=policy_data)
    response = client.get("/policies/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0] == policy_data

def test_get_policy_by_id():
    policy_data = {
        "id": 1,
        "policy_number": "12345",
        "policyholder_name": "John Doe",
        "policy_start_date": "2022-01-01",
        "policy_end_date": "2023-01-01"
    }
    client.post("/policies/", json=policy_data)
    response = client.get("/policies/1")
    assert response.status_code == 200
    assert response.json() == policy_data

def test_update_policy():
    policy_data = {
        "id": 1,
        "policy_number": "12345",
        "policyholder_name": "John Doe",
        "policy_start_date": "2022-01-01",
        "policy_end_date": "2023-01-01"
    }
    client.post("/policies/", json=policy_data)
    updated_policy_data = {
        "id": 1,
        "policy_number": "12346",
        "policyholder_name": "Jane Doe",
        "policy_start_date": "2022-01-01",
        "policy_end_date": "2023-01-01"
    }
    response = client.put("/policies/1", json=updated_policy_data)
    assert response.status_code == 200
    assert response.json() == updated_policy_data

def test_delete_policy():
    policy_data = {
        "id": 1,
        "policy_number": "12345",
        "policyholder_name": "John Doe",
        "policy_start_date": "2022-01-01",
        "policy_end_date": "2023-01-01"
    }
    client.post("/policies/", json=policy_data)
    response = client.delete("/policies/1")
    assert response.status_code == 204

def test_get_non_existent_policy():
    response = client.get("/policies/1")
    assert response.status_code == 404

def test_update_non_existent_policy():
    policy_data = {
        "id": 1,
        "policy_number": "12345",
        "policyholder_name": "John Doe",
        "policy_start_date": "2022-01-01",
        "policy_end_date": "2023-01-01"
    }
    response = client.put("/policies/1", json=policy_data)
    assert response.status_code == 404

def test_delete_non_existent_policy():
    response = client.delete("/policies/1")
    assert response.status_code == 404
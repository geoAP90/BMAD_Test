from fastapi import APIRouter, HTTPException
from src.models import Policy
from typing import List

router = APIRouter()

# In-memory storage
policies = {}

@router.get("/", response_model=List[Policy])
async def get_policies():
    return list(policies.values())

@router.post("/", response_model=Policy, status_code=201)
async def create_policy(policy: Policy):
    policies[policy.id] = policy
    return policy

@router.get("/{id}", response_model=Policy)
async def get_policy(id: int):
    if id not in policies:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policies[id]

@router.put("/{id}", response_model=Policy)
async def update_policy(id: int, policy: Policy):
    if id not in policies:
        raise HTTPException(status_code=404, detail="Policy not found")
    policies[id] = policy
    return policy

@router.delete("/{id}", status_code=204)
async def delete_policy(id: int):
    if id not in policies:
        raise HTTPException(status_code=404, detail="Policy not found")
    del policies[id]
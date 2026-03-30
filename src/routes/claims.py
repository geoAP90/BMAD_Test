from fastapi import APIRouter, HTTPException
from src.models import Claim
from typing import List

router = APIRouter()

# In-memory storage
claims = {}

@router.get("/", response_model=List[Claim])
async def get_claims():
    return list(claims.values())

@router.post("/", response_model=Claim, status_code=201)
async def create_claim(claim: Claim):
    if claim.id in claims:
        raise HTTPException(status_code=400, detail="Claim ID already exists")
    claims[claim.id] = claim
    return claim

@router.get("/{id}", response_model=Claim)
async def get_claim(id: int):
    if id not in claims:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claims[id]

@router.put("/{id}", response_model=Claim)
async def update_claim(id: int, claim: Claim):
    if id not in claims:
        raise HTTPException(status_code=404, detail="Claim not found")
    claims[id] = claim
    return claim

@router.delete("/{id}", status_code=204)
async def delete_claim(id: int):
    if id not in claims:
        raise HTTPException(status_code=404, detail="Claim not found")
    del claims[id]
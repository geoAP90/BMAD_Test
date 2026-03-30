from fastapi import APIRouter, HTTPException
from src.models import Payment
from typing import List

router = APIRouter()

# In-memory storage
payments = {}

@router.get("/", response_model=List[Payment])
async def get_payments():
    return list(payments.values())

@router.post("/", response_model=Payment, status_code=201)
async def create_payment(payment: Payment):
    payments[payment.id] = payment
    return payment

@router.get("/{id}", response_model=Payment)
async def get_payment(id: int):
    if id not in payments:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payments[id]

@router.put("/{id}", response_model=Payment)
async def update_payment(id: int, payment: Payment):
    if id not in payments:
        raise HTTPException(status_code=404, detail="Payment not found")
    payments[id] = payment
    return payment

@router.delete("/{id}", status_code=204)
async def delete_payment(id: int):
    if id not in payments:
        raise HTTPException(status_code=404, detail="Payment not found")
    del payments[id]
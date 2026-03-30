from pydantic import BaseModel, validator
from enum import Enum
from datetime import date
from typing import Optional

class ClaimStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Policy(BaseModel):
    id: int
    policy_number: str
    policy_holder: str
    policy_type: str
    start_date: date
    end_date: date

    @validator('start_date')
    def start_date_must_be_before_end_date(cls, v, values):
        if 'end_date' in values and v >= values['end_date']:
            raise ValueError('start_date must be before end_date')
        return v

class Claim(BaseModel):
    id: int
    policy_id: int
    claim_date: date
    claim_amount: float
    status: ClaimStatus = ClaimStatus.pending

class Payment(BaseModel):
    id: int
    claim_id: int
    payment_date: date
    payment_amount: float
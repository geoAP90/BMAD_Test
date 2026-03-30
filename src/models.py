from pydantic import BaseModel, Field
from enum import Enum
from datetime import date

class ClaimStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Policy(BaseModel):
    id: int = Field(..., title="Policy ID")
    policy_number: str = Field(..., title="Policy Number")
    policy_holder: str = Field(..., title="Policy Holder")
    policy_type: str = Field(..., title="Policy Type")
    start_date: date = Field(..., title="Start Date")
    end_date: date = Field(..., title="End Date")

class Claim(BaseModel):
    id: int = Field(..., title="Claim ID")
    policy_id: int = Field(..., title="Policy ID")
    claim_date: date = Field(..., title="Claim Date")
    claim_amount: float = Field(..., title="Claim Amount", ge=0)
    status: ClaimStatus = Field(..., title="Claim Status")

class Payment(BaseModel):
    id: int = Field(..., title="Payment ID")
    claim_id: int = Field(..., title="Claim ID")
    payment_date: date = Field(..., title="Payment Date")
    payment_amount: float = Field(..., title="Payment Amount", ge=0)
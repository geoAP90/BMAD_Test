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
    policyholder_name: str = Field(..., title="Policyholder Name")
    policy_start_date: date = Field(..., title="Policy Start Date")
    policy_end_date: date = Field(..., title="Policy End Date")

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
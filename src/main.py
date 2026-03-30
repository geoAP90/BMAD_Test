from fastapi import FastAPI
from src.routes import policies, claims, payments

app = FastAPI()

app.include_router(policies.router, prefix="/policies", tags=["policies"])
app.include_router(claims.router, prefix="/claims", tags=["claims"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
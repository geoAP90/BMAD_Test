from fastapi import FastAPI
from src.routes import policies, claims, payments

app = FastAPI(
    title="Insurance Claims API",
    description="API for managing insurance policies, claims, and payments",
    version="1.0.0",
)

app.include_router(policies.router, prefix="/policies", tags=["policies"])
app.include_router(claims.router, prefix="/claims", tags=["claims"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
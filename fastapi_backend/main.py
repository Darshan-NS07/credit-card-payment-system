from fastapi import FastAPI,Depends
from core.auth import get_current_user
from database.models import User
from routes.payments import router as payment_router
from routes.transactions import router as transaction_router


app = FastAPI(
    title="Credit Card Payment System - Payment API",
    description="FastAPI service for payment processing",
    version="1.0.0"
)

app.include_router(payment_router)
app.include_router(transaction_router)




@app.get("/")
def home():
    return {
        "message": "Credit Card Payment System Payment API is running"
    }

@app.get("/api/test-auth/")
def test_auth(
    current_user: User = Depends(get_current_user)
):

    return {
        "message": "JWT authentication successful.",
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }    
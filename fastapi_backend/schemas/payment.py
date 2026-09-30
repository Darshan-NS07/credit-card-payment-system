from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentRequest(BaseModel):

    card_id: int = Field(..., gt=0)

    amount: Decimal = Field(..., gt=0)

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3        
    )


class PaymentResponse(BaseModel):

    message: str
    transaction_id: int
    transaction_reference: str
    amount: float
    currency: str
    status: str
    failure_reason: str | None
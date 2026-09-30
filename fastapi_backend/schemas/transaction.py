from decimal import Decimal

from pydantic import BaseModel


class TransactionResponse(BaseModel):

    id: int
    card_id: int | None
    amount: Decimal
    currency: str
    status: str
    transaction_reference: str
    failure_reason: str | None
    created_at: str
    updated_at: str
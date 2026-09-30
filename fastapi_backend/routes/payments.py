from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.auth import get_current_user
from database.database import get_db
from database.models import User
from schemas.payment import PaymentRequest, PaymentResponse
from services.payment_service import process_payment


router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"]
)


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED
)
def make_payment(
    payment_data: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    transaction = process_payment(
        db=db,
        user_id=current_user.id,
        payment_data=payment_data
    )

    if transaction.status == "SUCCESS":

        message = "Payment successful."

    else:

        message = "Payment failed."

    return PaymentResponse(
        message=message,
        transaction_id=transaction.id,
        transaction_reference=transaction.transaction_reference,
        amount=transaction.amount,
        currency=transaction.currency,
        status=transaction.status,
        failure_reason=transaction.failure_reason
    )
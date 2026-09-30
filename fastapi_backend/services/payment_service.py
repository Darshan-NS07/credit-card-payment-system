import random
import uuid
from datetime import datetime,timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from database.models import Card, Transaction
from schemas.payment import PaymentRequest


def process_payment(
    db: Session,
    user_id: int,
    payment_data: PaymentRequest
):

    # ----- Check whether the card belongs to the logged-in user -----

    card = db.query(Card).filter(
        Card.id == payment_data.card_id,
        Card.user_id == user_id
    ).first()

    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found or does not belong to the user."
        )

    # ----- Generate unique transaction reference -----

    transaction_reference = (
        f"TXN-{uuid.uuid4().hex[:12].upper()}"
    )

    # ----- Create transaction with PENDING status -----

    transaction = Transaction(
        user_id=user_id,
        card_id=card.id,
        amount=payment_data.amount,
        currency=payment_data.currency.upper(),
        status="PENDING",
        transaction_reference=transaction_reference,
        failure_reason=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # ----- Simulate payment processing -----

    payment_success = random.choice([True, False])

    if payment_success:

        transaction.status = "SUCCESS"
        transaction.failure_reason = None

    else:

        transaction.status = "FAILED"
        transaction.failure_reason = "Payment simulation failed."

    # ----- Update transaction timestamp -----

    transaction.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(transaction)

    return transaction
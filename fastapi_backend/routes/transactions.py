from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.auth import get_current_user
from database.database import get_db
from database.models import Transaction, User
from schemas.transaction import TransactionResponse


router = APIRouter(
    prefix="/api/transactions",
    tags=["Transactions"]
)


@router.get(
    "/",
    response_model=list[TransactionResponse]
)
def get_transactions(
    status: str | None = Query(
        default=None,
        description="Filter by transaction status: PENDING, SUCCESS, or FAILED"
    ),

    min_amount: Decimal | None = Query(
        default=None,
        gt=0,
        description="Minimum transaction amount"
    ),

    max_amount: Decimal | None = Query(
        default=None,
        gt=0,
        description="Maximum transaction amount"
    ),

    start_date: date | None = Query(
        default=None,
        description="Filter transactions from this date"
    ),

    end_date: date | None = Query(
        default=None,
        description="Filter transactions up to this date"
    ),

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)
):

    # ----- Start with transactions belonging to logged-in user -----

    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    )

    # ----- Filter by status -----

    if status:

        status = status.upper()

        query = query.filter(
            Transaction.status == status
        )

    # ----- Filter by minimum amount -----

    if min_amount is not None:

        query = query.filter(
            Transaction.amount >= min_amount
        )

    # ----- Filter by maximum amount -----

    if max_amount is not None:

        query = query.filter(
            Transaction.amount <= max_amount
        )

    # ----- Filter by start date -----

    if start_date is not None:

        query = query.filter(
            Transaction.created_at >= start_date
        )

    # ----- Filter by end date -----

    if end_date is not None:

        query = query.filter(
            Transaction.created_at < end_date
        )

    # ----- Show newest transactions first -----

    transactions = query.order_by(
        Transaction.created_at.desc()
    ).all()

    # ----- Convert database records into API response -----

    return [
        TransactionResponse(
            id=transaction.id,
            card_id=transaction.card_id,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            transaction_reference=transaction.transaction_reference,
            failure_reason=transaction.failure_reason,
            created_at=transaction.created_at.isoformat(),
            updated_at=transaction.updated_at.isoformat()
        )
        for transaction in transactions
    ]
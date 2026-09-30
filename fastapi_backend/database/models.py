from datetime import datetime
from decimal import Decimal



from .database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String


class User(Base):
    __tablename__ = "users_user"

    id = Column(Integer, primary_key=True)
    password = Column(String(128), nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_superuser = Column(Integer, nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(10), nullable=False)
    is_active = Column(Integer, nullable=False)
    is_staff = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class Card(Base):
    __tablename__ = "cards_card"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users_user.id"), nullable=False)
    card_type = Column(String(10), nullable=False)
    cardholder_name = Column(String(100), nullable=False)
    masked_card_number = Column(String(19), nullable=False)
    last_four_digits = Column(String(4), nullable=False)
    expiry_month = Column(Integer, nullable=False)
    expiry_year = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class Transaction(Base):

    __tablename__ = "transactions_transaction"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users_user.id"),
        nullable=False
    )

    card_id = Column(
        Integer,
        ForeignKey("cards_card.id"),
        nullable=True
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False
    )

    currency = Column(
        String(3),
        nullable=False
    )

    status = Column(
        String(10),
        nullable=False
    )

    transaction_reference = Column(
        String(100),
        unique=True,
        nullable=False
    )

    failure_reason = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        nullable=False
    )
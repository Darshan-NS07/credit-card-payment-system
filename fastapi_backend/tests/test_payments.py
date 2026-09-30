import os

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base, get_db
from database.models import Card, Transaction, User
from main import app
from datetime import datetime


# ----- Create a separate test database connection -----

DATABASE_URL = (
    f"mysql://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ----- Override FastAPI database dependency -----

def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestPaymentAPI:

    def setup_method(self):

        self.db = TestingSessionLocal()

        # ----- Clean previous test data -----

        self.db.query(Transaction).filter(
            Transaction.user_id.in_([9001, 9002])
        ).delete(synchronize_session=False)

        self.db.query(Card).filter(
            Card.user_id.in_([9001, 9002])
        ).delete(synchronize_session=False)

        self.db.query(User).filter(
            User.id.in_([9001, 9002])
        ).delete(synchronize_session=False)

        self.db.commit()

        # ----- Create test user -----

        self.user = User(
          id=9001,
          password="test-password",
          first_name="Payment",
          last_name="Test",
          email="payment_test@example.com",
          role="USER",
          is_superuser=0,
          is_active=1,
          is_staff=0,
          created_at=datetime.now(),
          updated_at=datetime.now()
        )

        self.db.add(self.user)

        # ----- Create another test user -----

        self.other_user = User(
           id=9002,
           password="test-password",
           first_name="Other",
           last_name="User",
           email="other_payment_test@example.com",
           role="USER",
           is_superuser=0,
           is_active=1,
            is_staff=0,
           created_at=datetime.now(),
           updated_at=datetime.now()
        )

        self.db.add(self.other_user)

        self.db.commit()

        # ----- Create card for test user -----

        self.card = Card(
        user_id=self.user.id,
        card_type="CREDIT",
        cardholder_name="Payment Test",
        masked_card_number="************1111",
        last_four_digits="1111",
        expiry_month=10,
        expiry_year=2029,
        created_at=datetime.now(),
        updated_at=datetime.now()
        )

        self.db.add(self.card)

        # ----- Create card for another user -----

        self.other_card = Card(
        user_id=self.other_user.id,
        card_type="CREDIT",
        cardholder_name="Other User",
        masked_card_number="************2222",
        last_four_digits="2222",
        expiry_month=10,
        expiry_year=2029,
        created_at=datetime.now(),
        updated_at=datetime.now()
        )

        self.db.add(self.other_card)

        self.db.commit()

        self.db.refresh(self.card)
        self.db.refresh(self.other_card)

        # ----- Create JWT for test user -----

        secret_key = os.getenv("JWT_SECRET_KEY")

        payload = {
            "user_id": self.user.id,
            "token_type": "access"
        }

        self.access_token = jwt.encode(
            payload,
            secret_key,
            algorithm="HS256"
        )

        self.headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

    def teardown_method(self):

        # ----- Delete test transactions -----

        self.db.query(Transaction).filter(
            Transaction.user_id.in_([
                self.user.id,
                self.other_user.id
            ])
        ).delete(
            synchronize_session=False
        )

        # ----- Delete test cards -----

        self.db.query(Card).filter(
            Card.user_id.in_([
                self.user.id,
                self.other_user.id
            ])
        ).delete(
            synchronize_session=False
        )

        # ----- Delete test users -----

        self.db.query(User).filter(
            User.id.in_([
                self.user.id,
                self.other_user.id
            ])
        ).delete(
            synchronize_session=False
        )

        self.db.commit()
        self.db.close()

    # ----- Test successful payment request -----

    def test_valid_payment(self):

        response = client.post(
            "/api/payments/",
            headers=self.headers,
            json={
                "card_id": self.card.id,
                "amount": 1500.00,
                "currency": "INR"
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["transaction_id"] is not None
        assert data["transaction_reference"].startswith("TXN-")
        assert data["amount"] == 1500.00
        assert data["currency"] == "INR"
        assert data["status"] in [
            "SUCCESS",
            "FAILED"
        ]

    # ----- Test payment without JWT -----

    def test_payment_without_token(self):

        response = client.post(
            "/api/payments/",
            json={
                "card_id": self.card.id,
                "amount": 1500.00,
                "currency": "INR"
            }
        )

        assert response.status_code == 401

    # ----- Test payment using non-existent card -----

    def test_payment_with_invalid_card(self):

        response = client.post(
            "/api/payments/",
            headers=self.headers,
            json={
                "card_id": 999999,
                "amount": 1500.00,
                "currency": "INR"
            }
        )

        assert response.status_code == 404

    # ----- Test payment using another user's card -----

    def test_payment_with_other_users_card(self):

        response = client.post(
            "/api/payments/",
            headers=self.headers,
            json={
                "card_id": self.other_card.id,
                "amount": 1500.00,
                "currency": "INR"
            }
        )

        assert response.status_code == 404

    # ----- Test transaction is created -----

    def test_transaction_is_created(self):

        response = client.post(
            "/api/payments/",
            headers=self.headers,
            json={
                "card_id": self.card.id,
                "amount": 2500.00,
                "currency": "INR"
            }
        )

        assert response.status_code == 201

        data = response.json()

        self.db.rollback()
        
        transaction = self.db.query(Transaction).filter(
            Transaction.id == data["transaction_id"]
        ).first()

        assert transaction is not None

        assert transaction.user_id == self.user.id
        assert transaction.card_id == self.card.id
        assert transaction.amount == 2500
        assert transaction.currency == "INR"

    # ----- Test transaction reference is generated -----

    def test_transaction_reference(self):

        response = client.post(
            "/api/payments/",
            headers=self.headers,
            json={
                "card_id": self.card.id,
                "amount": 1000.00,
                "currency": "INR"
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["transaction_reference"].startswith(
            "TXN-"
        )

        assert len(
            data["transaction_reference"]
        ) == 16
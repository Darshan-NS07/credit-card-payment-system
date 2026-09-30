from decimal import Decimal

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from cards.models import Card
from users.models import User

from .models import Transaction


class TransactionManagementTests(APITestCase):

    def setUp(self):

        self.transaction_url = "/api/transactions/"

        # ----- Create first user -----

        self.user = User.objects.create_user(
            email="user1@example.com",
            password="Test@12345",
            first_name="User",
            last_name="One"
        )

        # ----- Create second user -----

        self.other_user = User.objects.create_user(
            email="user2@example.com",
            password="Test@12345",
            first_name="User",
            last_name="Two"
        )

        # ----- Create JWT for first user -----

        refresh = RefreshToken.for_user(self.user)

        self.access_token = str(refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

        # ----- Create card for first user -----

        self.card = Card.objects.create(
            user=self.user,
            card_type="CREDIT",
            cardholder_name="Test User",
            masked_card_number="************1111",
            last_four_digits="1111",
            expiry_month=10,
            expiry_year=2029
        )

        # ----- Create card for second user -----

        self.other_card = Card.objects.create(
            user=self.other_user,
            card_type="DEBIT",
            cardholder_name="Other User",
            masked_card_number="************2222",
            last_four_digits="2222",
            expiry_month=11,
            expiry_year=2029
        )


        # ----- Test authenticated user can view transaction history -----

    def test_view_transaction_history(self):

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("2500.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-TEST001",
            failure_reason=None
        )

        response = self.client.get(
            self.transaction_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data["transactions"]),
            1
        )

        self.assertEqual(
            response.data["transactions"][0]["transaction_reference"],
            "TXN-TEST001"
        )

        self.assertEqual(
            response.data["transactions"][0]["status"],
            "SUCCESS"
        )

    # ----- Test user can see only their own transactions -----

    def test_user_sees_only_own_transactions(self):

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("2500.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-USER001",
            failure_reason=None
        )

        Transaction.objects.create(
            user=self.other_user,
            card=self.other_card,
            amount=Decimal("5000.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-USER002",
            failure_reason=None
        )

        response = self.client.get(
            self.transaction_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        transactions = response.data["transactions"]

        self.assertEqual(
            len(transactions),
            1
        )

        self.assertEqual(
            transactions[0]["transaction_reference"],
            "TXN-USER001"
        )        

        # ----- Test unauthenticated user cannot view transactions -----

    def test_unauthenticated_user_cannot_view_transactions(self):

        self.client.credentials()

        response = self.client.get(
            self.transaction_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        # ----- Test user can view transaction details -----

    
    def test_view_transaction_details(self):

        transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("2500.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-DETAIL001",
            failure_reason=None
        )

        response = self.client.get(
            f"{self.transaction_url}{transaction.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        transaction_data = response.data["transaction"]

        self.assertEqual(
            transaction_data["transaction_reference"],
            "TXN-DETAIL001"
        )

        self.assertEqual(
            transaction_data["amount"],
            "2500.00"
        )

        self.assertEqual(
            transaction_data["status"],
            "SUCCESS"
        )

            # ----- Test user cannot view another user's transaction -----

    def test_cannot_view_other_users_transaction(self):

        transaction = Transaction.objects.create(
            user=self.other_user,
            card=self.other_card,
            amount=Decimal("5000.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-OTHER001",
            failure_reason=None
        )

        response = self.client.get(
            f"{self.transaction_url}{transaction.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        # ----- Test transaction status filter -----

    def test_filter_transactions_by_status(self):

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("1000.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-SUCCESS001",
            failure_reason=None
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("2000.00"),
            currency="INR",
            status="FAILED",
            transaction_reference="TXN-FAILED001",
            failure_reason="Payment failed."
        )

        response = self.client.get(
            self.transaction_url,
            {"status": "SUCCESS"}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        transactions = response.data["transactions"]

        self.assertEqual(
            len(transactions),
            1
        )

        self.assertEqual(
            transactions[0]["transaction_reference"],
            "TXN-SUCCESS001"
        )

        self.assertEqual(
            transactions[0]["status"],
            "SUCCESS"
        )

        # ----- Test transaction minimum amount filter -----

    def test_filter_transactions_by_min_amount(self):

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("1000.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-AMOUNT001",
            failure_reason=None
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("2500.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-AMOUNT002",
            failure_reason=None
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("5000.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-AMOUNT003",
            failure_reason=None
        )

        response = self.client.get(
            self.transaction_url,
            {"min_amount": "2000"}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        transactions = response.data["transactions"]

        self.assertEqual(
            len(transactions),
            2
        )

        amounts = [
            transaction["amount"]
            for transaction in transactions
        ]

        self.assertIn(
            "2500.00",
            amounts
        )

        self.assertIn(
            "5000.00",
            amounts
        )

        self.assertNotIn(
            "1000.00",
            amounts
        )

        # ----- Test transaction maximum amount filter -----

    def test_filter_transactions_by_max_amount(self):

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("1000.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-MAX001",
            failure_reason=None
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("2500.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-MAX002",
            failure_reason=None
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("5000.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-MAX003",
            failure_reason=None
        )

        response = self.client.get(
            self.transaction_url,
            {"max_amount": "3000"}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        transactions = response.data["transactions"]

        self.assertEqual(
            len(transactions),
            2
        )

        amounts = [
            transaction["amount"]
            for transaction in transactions
        ]

        self.assertIn(
            "1000.00",
            amounts
        )

        self.assertIn(
            "2500.00",
            amounts
        )

        self.assertNotIn(
            "5000.00",
            amounts
        )

        # ----- Test transaction start date filter -----

    def test_filter_transactions_by_start_date(self):

        old_transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("1000.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-DATE001",
            failure_reason=None
        )

        recent_transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("2000.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-DATE002",
            failure_reason=None
        )

        old_transaction.created_at = timezone.make_aware(
            timezone.datetime(
                2026,
                9,
                10,
                10,
                0,
                0
            )
        )

        old_transaction.save(
            update_fields=["created_at"]
        )

        recent_transaction.created_at = timezone.make_aware(
            timezone.datetime(
                2026,
                9,
                25,
                10,
                0,
                0
            )
        )

        recent_transaction.save(
            update_fields=["created_at"]
        )

        response = self.client.get(
            self.transaction_url,
            {"start_date": "2026-09-20"}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        transactions = response.data["transactions"]

        self.assertEqual(
            len(transactions),
            1
        )

        self.assertEqual(
            transactions[0]["transaction_reference"],
            "TXN-DATE002"
        )

        # ----- Test transaction end date filter -----

    def test_filter_transactions_by_end_date(self):

        old_transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("1000.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-END001",
            failure_reason=None
        )

        recent_transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("2000.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-END002",
            failure_reason=None
        )

        old_transaction.created_at = timezone.make_aware(
            timezone.datetime(
                2026,
                9,
                10,
                10,
                0,
                0
            )
        )

        old_transaction.save(
            update_fields=["created_at"]
        )

        recent_transaction.created_at = timezone.make_aware(
            timezone.datetime(
                2026,
                9,
                25,
                10,
                0,
                0
            )
        )

        recent_transaction.save(
            update_fields=["created_at"]
        )

        response = self.client.get(
            self.transaction_url,
            {"end_date": "2026-09-20"}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        transactions = response.data["transactions"]

        self.assertEqual(
            len(transactions),
            1
        )

        self.assertEqual(
            transactions[0]["transaction_reference"],
            "TXN-END001"
        )

        # ----- Test admin can export transactions as CSV -----

    def test_admin_can_export_transactions_csv(self):

        self.user.role = "ADMIN"
        self.user.is_staff = True
        self.user.save()

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=Decimal("2500.00"),
            currency="INR",
            status="SUCCESS",
            transaction_reference="TXN-CSV001",
            failure_reason=None
        )

        response = self.client.get(
            f"{self.transaction_url}export-csv/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response["Content-Type"],
            "text/csv"
        )

        self.assertIn(
            "transactions.csv",
            response["Content-Disposition"]
        )

        self.assertIn(
            "TXN-CSV001",
            response.content.decode()
        )

        self.assertIn(
            "user1@example.com",
            response.content.decode()
        )


        # ----- Test normal user cannot export transactions CSV -----

    def test_normal_user_cannot_export_transactions_csv(self):

        response = self.client.get(
            f"{self.transaction_url}export-csv/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )                
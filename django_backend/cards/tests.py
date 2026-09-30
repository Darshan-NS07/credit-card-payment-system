from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User

from .models import Card


class CardManagementTests(APITestCase):

    def setUp(self):

        self.card_url = "/api/cards/"

        self.user = User.objects.create_user(
            email="user1@example.com",
            password="Test@12345",
            first_name="User",
            last_name="One"
        )

        self.other_user = User.objects.create_user(
            email="user2@example.com",
            password="Test@12345",
            first_name="User",
            last_name="Two"
        )

        refresh = RefreshToken.for_user(self.user)

        self.access_token = str(refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

    # ----- Test adding a valid card -----

    def test_add_valid_card(self):

        response = self.client.post(
            self.card_url,
            {
                "card_type": "CREDIT",
                "cardholder_name": "Test User",
                "card_number": "4111111111111111",
                "expiry_month": 10,
                "expiry_year": 2029
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Card.objects.count(),
            1
        )

        card = Card.objects.first()

        self.assertEqual(
            card.last_four_digits,
            "1111"
        )

        self.assertEqual(
            card.masked_card_number,
            "************1111"
        )

    # ----- Test invalid card number -----

    def test_invalid_card_number(self):

        response = self.client.post(
            self.card_url,
            {
                "card_type": "CREDIT",
                "cardholder_name": "Test User",
                "card_number": "1234567890123456",
                "expiry_month": 10,
                "expiry_year": 2029
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Card.objects.count(),
            0
        )

    # ----- Test expired card -----

    def test_expired_card(self):

        response = self.client.post(
            self.card_url,
            {
                "card_type": "CREDIT",
                "cardholder_name": "Test User",
                "card_number": "4111111111111111",
                "expiry_month": 1,
                "expiry_year": 2020
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ----- Test CVV is not accepted -----

    def test_cvv_is_not_accepted(self):

        response = self.client.post(
            self.card_url,
            {
                "card_type": "CREDIT",
                "cardholder_name": "Test User",
                "card_number": "4111111111111111",
                "cvv": "123",
                "expiry_month": 10,
                "expiry_year": 2029
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ----- Test user can view own cards -----

    def test_view_own_cards(self):

        Card.objects.create(
            user=self.user,
            card_type="CREDIT",
            cardholder_name="Test User",
            masked_card_number="************1111",
            last_four_digits="1111",
            expiry_month=10,
            expiry_year=2029
        )

        response = self.client.get(
            self.card_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data["cards"]),
            1
        )

        self.assertEqual(
            response.data["cards"][0]["last_four_digits"],
            "1111"
        )

    # ----- Test user sees only their own cards -----

    def test_user_sees_only_own_cards(self):

        Card.objects.create(
            user=self.user,
            card_type="CREDIT",
            cardholder_name="User One",
            masked_card_number="************1111",
            last_four_digits="1111",
            expiry_month=10,
            expiry_year=2029
        )

        Card.objects.create(
            user=self.other_user,
            card_type="DEBIT",
            cardholder_name="User Two",
            masked_card_number="************2222",
            last_four_digits="2222",
            expiry_month=11,
            expiry_year=2029
        )

        response = self.client.get(
            self.card_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data["cards"]),
            1
        )

        self.assertEqual(
            response.data["cards"][0]["last_four_digits"],
            "1111"
        )

    # ----- Test deleting own card -----

    def test_delete_own_card(self):

        card = Card.objects.create(
            user=self.user,
            card_type="CREDIT",
            cardholder_name="Test User",
            masked_card_number="************1111",
            last_four_digits="1111",
            expiry_month=10,
            expiry_year=2029
        )

        response = self.client.delete(
            f"{self.card_url}{card.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertFalse(
            Card.objects.filter(id=card.id).exists()
        )

    # ----- Test user cannot delete another user's card -----

    def test_cannot_delete_other_users_card(self):

        card = Card.objects.create(
            user=self.other_user,
            card_type="CREDIT",
            cardholder_name="User Two",
            masked_card_number="************2222",
            last_four_digits="2222",
            expiry_month=11,
            expiry_year=2029
        )

        response = self.client.delete(
            f"{self.card_url}{card.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertTrue(
            Card.objects.filter(id=card.id).exists()
        )


            # ----- Test unauthenticated user cannot view cards -----

    def test_unauthenticated_user_cannot_view_cards(self):

        self.client.credentials()

        response = self.client.get(
            self.card_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        # ----- Test empty cardholder name ----- 

    def test_empty_cardholder_name(self):

        response = self.client.post(
            self.card_url,
            {
                "card_type": "CREDIT",
                "cardholder_name": "",
                "card_number": "4111111111111111",
                "expiry_month": 10,
                "expiry_year": 2029
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Card.objects.count(),
            0
        )


         # ----- Test invalid expiry month -----

    def test_invalid_expiry_month(self):

        response = self.client.post(
            self.card_url,
            {
                "card_type": "CREDIT",
                "cardholder_name": "Test User",
                "card_number": "4111111111111111",
                "expiry_month": 13,
                "expiry_year": 2029
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Card.objects.count(),
            0
        )   


        # ----- Test full card number is not returned ----- 

    def test_full_card_number_is_not_returned(self):

        response = self.client.post(
            self.card_url,
            {
                "card_type": "CREDIT",
                "cardholder_name": "Test User",
                "card_number": "4111111111111111",
                "expiry_month": 10,
                "expiry_year": 2029
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        response_data = response.data["card"]

        self.assertNotIn(
            "card_number",
            response_data
        )

        self.assertNotIn(
            "4111111111111111",
            str(response_data)
        )

        self.assertEqual(
            response_data["last_four_digits"],
            "1111"
        )

        self.assertEqual(
            response_data["masked_card_number"],
            "************1111"
        )
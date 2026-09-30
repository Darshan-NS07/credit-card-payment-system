from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class AuthenticationTests(APITestCase):

    def setUp(self):

        self.register_url = "/api/auth/register/"
        self.login_url = "/api/auth/login/"
        self.profile_url = "/api/auth/profile/"
        self.refresh_url = "/api/auth/token/refresh/"
        self.logout_url = "/api/auth/logout/"

        self.user_data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "Test@12345",
            "password_confirm": "Test@12345",
        }

    # ----- Test successful registration -----

    def test_user_registration(self):

        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            User.objects.filter(
                email="testuser@example.com"
            ).exists()
        )

    # ----- Test duplicate email registration -----

    def test_duplicate_email_registration(self):

        User.objects.create_user(
            email="testuser@example.com",
            password="Test@12345",
            first_name="Existing",
            last_name="User"
        )

        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        # ----- Test invalid email registration -----

    def test_invalid_email_registration(self):

        invalid_data = self.user_data.copy()

        invalid_data["email"] = "invalid-email"

        response = self.client.post(
            self.register_url,
            invalid_data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        ) 


        # ----- Test password confirmation mismatch -----

    def test_password_confirmation_mismatch(self):

        invalid_data = self.user_data.copy()

        invalid_data["password_confirm"] = "Different@12345"

        response = self.client.post(
            self.register_url,
            invalid_data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )   

    # ----- Test successful login -----

    def test_successful_login(self):

        User.objects.create_user(
            email="testuser@example.com",
            password="Test@12345",
            first_name="Test",
            last_name="User"
        )

        response = self.client.post(
            self.login_url,
            {
                "email": "testuser@example.com",
                "password": "Test@12345"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            "access",
            response.data
        )

        self.assertIn(
            "refresh",
            response.data
        )

        # ----- Test successful token refresh -----

    def test_token_refresh(self):

        User.objects.create_user(
            email="testuser@example.com",
            password="Test@12345",
            first_name="Test",
            last_name="User"
        )

        login_response = self.client.post(
            self.login_url,
            {
                "email": "testuser@example.com",
                "password": "Test@12345"
            },
            format="json"
        )

        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": refresh_token
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            "access",
            response.data
        )    

    # ----- Test invalid login -----

    def test_invalid_login(self):

        User.objects.create_user(
            email="testuser@example.com",
            password="Test@12345",
            first_name="Test",
            last_name="User"
        )

        response = self.client.post(
            self.login_url,
            {
                "email": "testuser@example.com",
                "password": "WrongPassword@123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # ----- Test profile without authentication -----

    def test_profile_without_token(self):

        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # ----- Test profile with valid JWT -----

    def test_profile_with_token(self):

        User.objects.create_user(
            email="testuser@example.com",
            password="Test@12345",
            first_name="Test",
            last_name="User"
        )

        login_response = self.client.post(
            self.login_url,
            {
                "email": "testuser@example.com",
                "password": "Test@12345"
            },
            format="json"
        )

        access_token = login_response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["email"],
            "testuser@example.com"
        )

    # ----- Test logout and refresh-token blacklist -----

    def test_logout_blacklists_refresh_token(self):

        User.objects.create_user(
            email="testuser@example.com",
            password="Test@12345",
            first_name="Test",
            last_name="User"
        )

        login_response = self.client.post(
            self.login_url,
            {
                "email": "testuser@example.com",
                "password": "Test@12345"
            },
            format="json"
        )

        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        logout_response = self.client.post(
            self.logout_url,
            {
                "refresh": refresh_token
            },
            format="json"
        )

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_200_OK
        )

        # ----- Try to use the blacklisted refresh token -----

        refresh_response = self.client.post(
            self.refresh_url,
            {
                "refresh": refresh_token
            },
            format="json"
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
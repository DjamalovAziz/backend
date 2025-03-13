# backend\message\tests.py:

import json
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import PasswordResetCode

# ~~~~~~~~~~~~~~~~~~~~ MESSAGE ~~~~~~~~~~~~~~~~~~~~
User = get_user_model()


class PasswordResetTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpassword",
            phone_number="+1234567890",
            telegram_chat_id="123456789",
        )

        self.client = APIClient()

        # URLs
        self.reset_init_url = reverse("message:reset-password-init")
        self.reset_confirm_url = reverse("message:reset-password-confirm")

    def test_reset_password_nonexistent_user(self):
        """Test attempting to reset password for a nonexistent user"""
        response = self.client.post(
            self.reset_init_url,
            {"email": "nonexistent@example.com", "delivery_method": "email"},
        )

        # Should still return 200 OK to prevent email enumeration
        self.assertEqual(response.status_code, 200)

        # But no reset code should be created
        self.assertEqual(PasswordResetCode.objects.count(), 0)

    @patch("message.tasks.send_email_code")
    def test_reset_password_via_email_success(self, mock_send_email):
        """Test successful password reset via email"""
        mock_send_email.return_value = True

        # Initiate reset
        response = self.client.post(
            self.reset_init_url,
            {"email": "test@example.com", "delivery_method": "email"},
        )

        self.assertEqual(response.status_code, 200)

        # Verify a reset code was created
        self.assertEqual(PasswordResetCode.objects.count(), 1)
        reset_code = PasswordResetCode.objects.get(user=self.user)
        self.assertEqual(reset_code.delivery_method, "email")

        # Verify the code was sent
        mock_send_email.assert_called_once()

        # Complete the reset
        response = self.client.post(
            self.reset_confirm_url,
            {
                "email": "test@example.com",
                "code": reset_code.code,
                "new_password": "newpassword123",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

        # Verify the code is marked as used
        reset_code.refresh_from_db()
        self.assertTrue(reset_code.is_used)

    @patch("message.tasks.send_sms_code")
    def test_reset_password_via_sms_success(self, mock_send_sms):
        """Test successful password reset via SMS"""
        mock_send_sms.return_value = True

        # Initiate reset
        response = self.client.post(
            self.reset_init_url, {"email": "test@example.com", "delivery_method": "sms"}
        )

        self.assertEqual(response.status_code, 200)

        # Verify a reset code was created
        self.assertEqual(PasswordResetCode.objects.count(), 1)
        reset_code = PasswordResetCode.objects.get(user=self.user)
        self.assertEqual(reset_code.delivery_method, "sms")

        # Verify the code was sent
        mock_send_sms.assert_called_once()

        # Complete the reset
        response = self.client.post(
            self.reset_confirm_url,
            {
                "email": "test@example.com",
                "code": reset_code.code,
                "new_password": "newpassword123",
            },
        )

        self.assertEqual(response.status_code, 200)

    @patch("message.tasks.send_telegram_code")
    def test_reset_password_via_telegram_success(self, mock_send_telegram):
        """Test successful password reset via Telegram"""
        mock_send_telegram.return_value = True

        # Initiate reset
        response = self.client.post(
            self.reset_init_url,
            {"email": "test@example.com", "delivery_method": "telegram"},
        )

        self.assertEqual(response.status_code, 200)

        # Verify a reset code was created
        self.assertEqual(PasswordResetCode.objects.count(), 1)
        reset_code = PasswordResetCode.objects.get(user=self.user)
        self.assertEqual(reset_code.delivery_method, "telegram")

        # Verify the code was sent
        mock_send_telegram.assert_called_once()

        # Complete the reset
        response = self.client.post(
            self.reset_confirm_url,
            {
                "email": "test@example.com",
                "code": reset_code.code,
                "new_password": "newpassword123",
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_reset_password_invalid_code(self):
        """Test password reset with invalid code"""
        # Create a valid reset code
        reset_code = PasswordResetCode.objects.create(
            user=self.user, code="123456", delivery_method="email"
        )

        # Attempt to reset with wrong code
        response = self.client.post(
            self.reset_confirm_url,
            {
                "email": "test@example.com",
                "code": "999999",  # Wrong code
                "new_password": "newpassword123",
            },
        )

        self.assertEqual(response.status_code, 400)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("oldpassword"))

        # Verify attempt count increased
        reset_code.refresh_from_db()
        self.assertEqual(reset_code.attempts, 1)

    def test_reset_password_expired_code(self):
        """Test password reset with expired code"""
        # Create an expired reset code
        expired_time = timezone.now() - timedelta(minutes=15)  # 15 minutes ago
        reset_code = PasswordResetCode.objects.create(
            user=self.user,
            code="123456",
            delivery_method="email",
            created_at=expired_time,
            expires_at=expired_time + timedelta(minutes=10),  # Expired 5 minutes ago
        )

        # Attempt to reset with expired code
        response = self.client.post(
            self.reset_confirm_url,
            {
                "email": "test@example.com",
                "code": "123456",
                "new_password": "newpassword123",
            },
        )

        self.assertEqual(response.status_code, 400)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("oldpassword"))

    def test_reset_password_max_attempts(self):
        """Test password reset with maximum attempts reached"""
        # Create a reset code with 3 attempts already used
        reset_code = PasswordResetCode.objects.create(
            user=self.user, code="123456", delivery_method="email", attempts=3
        )

        # Attempt to reset
        response = self.client.post(
            self.reset_confirm_url,
            {
                "email": "test@example.com",
                "code": "123456",  # Correct code but max attempts reached
                "new_password": "newpassword123",
            },
        )

        self.assertEqual(response.status_code, 400)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("oldpassword"))

    @patch("message.tasks.send_email_code")
    def test_unavailable_delivery_method(self, mock_send_email):
        """Test attempt to use unavailable delivery method"""
        # Remove the user's phone number
        self.user.phone_number = ""
        self.user.save()

        # Attempt to reset via SMS
        response = self.client.post(
            self.reset_init_url, {"email": "test@example.com", "delivery_method": "sms"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("not available", response.data["detail"])

        # Verify no reset code was created
        self.assertEqual(PasswordResetCode.objects.count(), 0)

        # Verify no code was sent
        mock_send_email.assert_not_called()

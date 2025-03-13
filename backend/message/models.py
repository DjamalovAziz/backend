# backend\message\models.py:

from django.db import models
from django.conf import settings
from django.utils import timezone

#
import random
import string

# ~~~~~~~~~~~~~~~~~~~~ MESSAGE ~~~~~~~~~~~~~~~~~~~~


class PasswordResetCode(models.Model):
    """
    Model to store password reset codes and their status
    """

    DELIVERY_METHODS = [
        ("telegram", "Telegram"),
        ("sms", "SMS"),
        ("email", "Email"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reset_codes"
    )
    code = models.CharField(max_length=6)
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_METHODS)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Password Reset Code"
        verbose_name_plural = "Password Reset Codes"

    def __str__(self):
        return f"Reset code for {self.user.email} via {self.delivery_method}"

    def save(self, *args, **kwargs):
        # Set expiration time to 10 minutes from now if not set
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if the code is valid (not expired, not used, and attempts < 3)"""
        return (
            not self.is_used and self.attempts < 3 and timezone.now() < self.expires_at
        )

    @classmethod
    def generate_code(cls):
        """Generate a random 6-digit code"""
        return "".join(random.choices(string.digits, k=6))

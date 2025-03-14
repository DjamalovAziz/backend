# backend\message\models.py:

from django.db import models
from django.conf import settings
from django.utils import timezone

#
import random
import string

# ~~~~~~~~~~~~~~~~~~~~ MESSAGE ~~~~~~~~~~~~~~~~~~~~


class PasswordResetCode(models.Model):
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
        return f"Reset code for {self.user.username} via {self.delivery_method}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        return (
            not self.is_used and self.attempts < 3 and timezone.now() < self.expires_at
        )

    @classmethod
    def generate_code(cls):
        return "".join(random.choices(string.digits, k=6))

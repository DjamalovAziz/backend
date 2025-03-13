# backend\message\signals.py:

# ~~~~~~~~~~~~~~~~~~~~ MESSAGE ~~~~~~~~~~~~~~~~~~~~

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from .models import PasswordResetCode


@receiver(post_save, sender=PasswordResetCode)
def cleanup_old_reset_codes(sender, instance, created, **kwargs):
    """
    Clean up old password reset codes when a new one is created
    """
    if created:
        # Delete expired codes for this user
        PasswordResetCode.objects.filter(
            user=instance.user, expires_at__lt=timezone.now()
        ).delete()

        # Keep only the last N codes for this user
        codes_to_keep = 5
        old_codes = PasswordResetCode.objects.filter(user=instance.user).order_by(
            "-created_at"
        )[codes_to_keep:]

        for code in old_codes:
            code.delete()

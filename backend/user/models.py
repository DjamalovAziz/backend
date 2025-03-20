# backend\user\models.py:

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.conf import settings

#
import os
import uuid


def avatar_upload_path(instance, filename):
    # For Avatar model
    if hasattr(instance, "user"):
        user_id = str(instance.user.uuid)
        ext = filename.split(".")[-1]
        new_filename = f"{uuid.uuid4()}.{ext}"
        return os.path.join("avatars", user_id, new_filename)
    # For User model (single avatar scenario)
    else:
        ext = filename.split(".")[-1]
        new_filename = f"{instance.uuid}.{ext}"
        return os.path.join("avatars", new_filename)


# For Multiple Avatar scenario
class Avatar(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="avatars")
    image = models.ImageField(
        upload_to=avatar_upload_path,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_primary", "-created_at"]

    def __str__(self):
        return f"Avatar for {self.user.username}"

    def save(self, *args, **kwargs):
        # If setting this avatar as primary, unset all other primary avatars
        if self.is_primary:
            Avatar.objects.filter(user=self.user, is_primary=True).update(
                is_primary=False
            )

        # If this is the only avatar, make it primary
        if not self.pk and not Avatar.objects.filter(user=self.user).exists():
            self.is_primary = True

        super().save(*args, **kwargs)


def avatar_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    new_filename = f"{instance.uuid}.{ext}"
    return os.path.join("avatars", new_filename)


class User(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="Email address")

    username = models.CharField(max_length=150, unique=True)

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    telegram_chat_id = models.CharField(max_length=100, blank=True, null=True)
    telegram_username = models.CharField(max_length=100, blank=True, null=True)

    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username

    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return "/media/avatars/default/PROFILE.jpg"

    def get_primary_avatar_url(self):
        primary_avatar = self.avatars.filter(is_primary=True).first()
        if primary_avatar:
            return primary_avatar.image.url
        return "/media/avatars/default/PROFILE.jpg"

    # def get_avatar_url(self):
    # if settings.AVATAR_MULTIPLE_MODE:
    #     # Multiple Avatar сценарий
    #     return self.get_primary_avatar_url()
    # else:
    #     # Single Avatar сценарий
    #     if self.avatar and hasattr(self.avatar, "url"):
    #         return self.avatar.url
    #     return settings.AVATAR_DEFAULT_PATH

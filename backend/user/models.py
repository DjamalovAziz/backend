# backend\user\models.py:

from django.contrib.auth.models import AbstractUser
from django.db import models

#
import uuid

# ~~~~~~~~~~~~~~~~~~~~ User ~~~~~~~~~~~~~~~~~~~~


class User(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="Email address")

    username = models.CharField(max_length=150, blank=True, null=True, unique=True)

    phone_number = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import uuid


class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)

    # Указываем уникальные related_name для групп и разрешений
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # уникальное имя
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",  # уникальное имя
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username
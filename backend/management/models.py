# backend\management\models.py:

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models

#
import uuid

#
from core.common import RelationType, UserRole
from organization.models import Branch, Organization


# ~~~~~~~~~~~~~~~~~~~~ User ~~~~~~~~~~~~~~~~~~~~


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=50, unique=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# ~~~~~~~~~~~~~~~~~~~~ Relation ~~~~~~~~~~~~~~~~~~~~


class Relation(models.Model):

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_role = models.CharField(
        max_length=50, choices=UserRole.choices, default=UserRole.WORKER
    )
    relation_type = models.CharField(
        max_length=50, choices=RelationType.choices, default=RelationType.RELATION
    )

    def __str__(self):
        return f"{self.user} - {self.user_role} - {self.relation_type} in {self.branch} of {self.organization}"

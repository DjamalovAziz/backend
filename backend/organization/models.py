# backend\organization\models.py:

import uuid
from django.db import models
from django.conf import settings
from core.common import UserRole, RelationType


# ~~~~~~~~~~~~~~~~~~~~ ORGANIZATION ~~~~~~~~~~~~~~~~~~~~

class Organization(models.Model):
    """
    Organization model to represent a company or business entity.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_organizations",
    )

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name


# ~~~~~~~~~~~~~~~~~~~~ BRANCH ~~~~~~~~~~~~~~~~~~~~

class Branch(models.Model):
    """
    Branch model to represent different locations or departments within an organization.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="branches"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_branches",
    )

    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"

    def __str__(self):
        return f"{self.name} - {self.organization.name}"

# ~~~~~~~~~~~~~~~~~~~~ RELATION ~~~~~~~~~~~~~~~~~~~~

class Relation(models.Model):
    """
    Relation model to represent the relationship between users, branches, and organizations.
    This handles user roles and different types of relationships (requests, invitations, actual relations).
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="relations"
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="relations"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="relations"
    )
    user_role = models.CharField(
        max_length=50, choices=UserRole.choices, default=UserRole.WORKER
    )
    relation_type = models.CharField(
        max_length=50, choices=RelationType.choices, default=RelationType.RELATION
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Relation"
        verbose_name_plural = "Relations"
        # Ensure a user can only have one relation of a specific type with a branch
        unique_together = ["user", "branch", "relation_type"]

    def __str__(self):
        return f"{self.user} - {self.branch.name} - {self.get_relation_type_display()}"

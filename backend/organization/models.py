# backend\organization\models.py:

from django.db import models

#
import uuid

# ~~~~~~~~~~~~~~~~~~~~ Organization ~~~~~~~~~~~~~~~~~~~~


class Organization(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.name


# ~~~~~~~~~~~~~~~~~~~~ Branch ~~~~~~~~~~~~~~~~~~~~


class Branch(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=100)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="branches"
    )

    def __str__(self):
        return f"{self.name} - {self.organization}"

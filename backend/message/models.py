# backend\message\models.py:

from django.db import models

#
import uuid


# ~~~~~~~~~~~~~~~~~~~~ Notification ~~~~~~~~~~~~~~~~~~~~
class Notification(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    text = models.TextField(unique=True, max_length=100)

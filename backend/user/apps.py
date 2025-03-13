# backend\user\apps.py:

from django.apps import AppConfig


# ~~~~~~~~~~~~~~~~~~~~ USER ~~~~~~~~~~~~~~~~~~~~
class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user"

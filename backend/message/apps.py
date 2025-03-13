# backend\message\apps.py:

from django.apps import AppConfig

# ~~~~~~~~~~~~~~~~~~~~ MESSAGE ~~~~~~~~~~~~~~~~~~~~


class MessageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "message"

    def ready(self):
        # Import signals to ensure they are registered
        import message.signals

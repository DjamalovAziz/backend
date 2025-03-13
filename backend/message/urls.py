# backend\message\urls.py:

# ~~~~~~~~~~~~~~~~~~~~ MESSAGE ~~~~~~~~~~~~~~~~~~~~

from django.urls import path
from . import views

app_name = "message"

urlpatterns = [
    path("reset-password/", views.reset_password_init, name="reset-password-init"),
    path(
        "reset-password/confirm/",
        views.reset_password_confirm,
        name="reset-password-confirm",
    ),
]

# backend\message\admin.py:

from django.contrib import admin
from .models import PasswordResetCode

# ~~~~~~~~~~~~~~~~~~~~ MESSAGE ~~~~~~~~~~~~~~~~~~~~


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "delivery_method",
        "created_at",
        "expires_at",
        "is_used",
        "attempts",
    )
    list_filter = ("delivery_method", "is_used")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("code", "created_at", "expires_at")
    date_hierarchy = "created_at"

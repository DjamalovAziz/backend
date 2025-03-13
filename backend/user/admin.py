# backend\user\admin.py:

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

#
from .models import User

# ~~~~~~~~~~~~~~~~~~~~ USER ~~~~~~~~~~~~~~~~~~~~


class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "username",
        "phone_number",
        "is_staff",
        "is_active",
        "avatar_preview",
    )
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "username", "phone_number")
    ordering = ("email", "username")

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.avatar.url,
            )
        return format_html("<span>No Avatar</span>")

    avatar_preview.short_description = "Avatar"

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "phone_number", "avatar")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)

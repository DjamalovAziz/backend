# backend\organization\admin.py:

# backend/organization/admin.py

from django.contrib import admin
from .models import Organization, Branch, Relation


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "created_by")
    list_filter = ("created_at",)
    search_fields = ("name", "description")
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("uuid", "name", "description", "created_by")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "created_at", "created_by")
    list_filter = ("organization", "created_at")
    search_fields = ("name", "description", "organization__name")
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {"fields": ("uuid", "name", "description", "organization", "created_by")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "organization",
        "branch",
        "user_role",
        "relation_type",
        "created_at",
    )
    list_filter = ("user_role", "relation_type", "created_at")
    search_fields = ("user__email", "organization__name", "branch__name")
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("uuid", "user", "organization", "branch")}),
        ("Role & Relation Type", {"fields": ("user_role", "relation_type")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

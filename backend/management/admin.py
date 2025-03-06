# backend\management\admin.py:

from django.contrib import admin
from django.contrib.auth import get_user_model

#
from management.models import Relation

# ~~~~~~~~~~~~~~~~~~~~ User ~~~~~~~~~~~~~~~~~~~~
User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "last_login", "is_staff")
    list_filter = ("is_staff", "is_superuser")
    search_fields = ("email",)


admin.site.register(User, UserAdmin)


# ~~~~~~~~~~~~~~~~~~~~ Relation ~~~~~~~~~~~~~~~~~~~~
admin.site.register(Relation)

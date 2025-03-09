# backend\organization\admin.py:

from django.contrib import admin

#
from .models import Branch, Organization

admin.site.register(Organization)
admin.site.register(Branch)

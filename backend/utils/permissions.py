# backend\utils\permissions.py:

from rest_framework import permissions
from django.db.models import Q
#
from organization.models import Organization, Branch, Relation
from utils.enamurations import UserRole, RelationType

# ~~~~~~~~~~~~~~~~~~~~ USER ~~~~~~~~~~~~~~~~~~~~


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.uuid == request.user.uuid

# ~~~~~~~~~~~~~~~~~~~~ ORGANIZATION ~~~~~~~~~~~~~~~~~~~~


class IsOwnerOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, "created_by") and obj.created_by == request.user:
            return True

        if isinstance(obj, Organization):
            return Relation.objects.filter(
                organization=obj,
                user=request.user,
                user_role=UserRole.ORGANIZATION_OWNER,
                relation_type=RelationType.RELATION,
            ).exists()

        if isinstance(obj, Branch):
            return Relation.objects.filter(
                Q(branch=obj, user_role=UserRole.BRANCH_MANAGER)
                | Q(
                    organization=obj.organization, user_role=UserRole.ORGANIZATION_OWNER
                ),
                user=request.user,
                relation_type=RelationType.RELATION,
            ).exists()

        return False

# backend\organization\permissions.py:

from rest_framework import permissions
from django.db.models import Q
#
from  .models import Organization, Branch, Relation
from core.common import UserRole, RelationType

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if the user is the owner of the object or has admin rights.
    """

    def has_object_permission(self, request, view, obj):
        # Allow read permissions for all users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user created this object
        if hasattr(obj, "created_by") and obj.created_by == request.user:
            return True

        # For organizations, check if the user is the organization owner
        if isinstance(obj, Organization):
            return Relation.objects.filter(
                organization=obj,
                user=request.user,
                user_role=UserRole.ORGANIZATION_OWNER,
                relation_type=RelationType.RELATION,
            ).exists()

        # For branches, check if the user is the branch manager or organization owner
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
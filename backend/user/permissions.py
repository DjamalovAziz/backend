# backend\user\permissions.py:

from rest_framework import permissions

# ~~~~~~~~~~~~~~~~~~~~ USER ~~~~~~~~~~~~~~~~~~~~


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.uuid == request.user.uuid


# class AllowGetRequests(permissions.BasePermission):
#     """
#     Custom permission to allow GET requests without authentication.
#     """

#     def has_permission(self, request, view):
#         if request.method == "GET":
#             return True
#         return request.user and request.user.is_authenticated

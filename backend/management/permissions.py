# backend\management\permissions.py:

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только владельцу объекта изменять его.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить GET, HEAD, OPTIONS запросы для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешить изменение объекта только его владельцу
        return obj == request.user

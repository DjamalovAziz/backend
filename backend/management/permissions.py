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


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Разрешает GET-запросы всем пользователям, но требует аутентификацию для других методов.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user and request.user.is_authenticated

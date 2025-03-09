# backend\management\urls.py:

from django.urls import path, include

#
from rest_framework.routers import DefaultRouter
from .views import (
    RelationViewSet,
    UserViewSet,
    ChangePasswordView,
    SignupView,
    SigninView,
    LogoutView,
    CustomTokenRefreshView,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"relations", RelationViewSet)

urlpatterns = [
    path("users/signup/", SignupView.as_view(), name="signup"),
    path("users/signin/", SigninView.as_view(), name="signin"),
    path("users/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("users/logout/", LogoutView.as_view(), name="logout"),
    path("", include(router.urls)),
    path(
        "users/<uuid:pk>/change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
]

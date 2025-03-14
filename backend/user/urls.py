# backend\user\urls.py:

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserViewSet, CustomTokenObtainPairView

# ~~~~~~~~~~~~~~~~~~~~ USER ~~~~~~~~~~~~~~~~~~~~
router = DefaultRouter()
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("users/signin/", CustomTokenObtainPairView.as_view(), name="signin"),
    path("users/refresh_token/", TokenRefreshView.as_view(), name="refresh_token"),
    path("", include(router.urls)),
]

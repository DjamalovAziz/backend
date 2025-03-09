# backend\message\urls.py:

from django.urls import include, path
from rest_framework.routers import DefaultRouter

#
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet)

urlpatterns = [path("", include(router.urls))]

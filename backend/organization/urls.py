# backend\organization\urls.py:

from django.urls import path, include
from rest_framework.routers import DefaultRouter

#
from .views import BranchViewSet, OrganizationViewSet

router = DefaultRouter()
router.register(r"organizations", OrganizationViewSet)
router.register(r"branchs", BranchViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

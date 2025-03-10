# backend\organization\urls.py:

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrganizationViewSet, BranchViewSet, RelationViewSet

router = DefaultRouter()
router.register("organizations", OrganizationViewSet)
router.register("branches", BranchViewSet)
router.register("relations", RelationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

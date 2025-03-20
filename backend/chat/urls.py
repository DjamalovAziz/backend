# backend\chat\urls.py:

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"personal", views.PersonalChatViewSet, basename="personal-chat")
router.register(r"groups", views.GroupChatViewSet, basename="group-chat")

urlpatterns = [
    path("", include(router.urls)),
]

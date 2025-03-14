# backend\chat\urls.py:

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChannelViewSet, GroupViewSet, MessageViewSet

router = DefaultRouter()
router.register('channels', ChannelViewSet, basename='channels')
router.register('groups', GroupViewSet, basename='groups')
router.register('messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)),
]
# backend\chat\routing.py:

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/chat/personal/(?P<chat_uuid>[0-9a-f-]+)/$",
        consumers.PersonalChatConsumer.as_asgi(),
    ),
    re_path(
        r"ws/chat/group/(?P<chat_uuid>[0-9a-f-]+)/$",
        consumers.GroupChatConsumer.as_asgi(),
    ),
]

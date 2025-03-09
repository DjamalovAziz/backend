# backend\message\views.py:

from rest_framework import viewsets

#
from message.models import Notification
from message.serializers import NotificationSerializer


# ~~~~~~~~~~~~~~~~~~~~ Notification ~~~~~~~~~~~~~~~~~~~~
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

# backend\message\serializers.py:

from rest_framework import serializers

#
from message.models import Notification

# ~~~~~~~~~~~~~~~~~~~~ Notification ~~~~~~~~~~~~~~~~~~~~


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["uuid", "text"]

# backend\chat\serializers.py:

from rest_framework import serializers
from .models import Channel, Group, Message
from user.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['uuid', 'content', 'created_at', 'sender', 'is_read']
        read_only_fields = ['uuid', 'created_at', 'is_read']

class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Group
        fields = ['uuid', 'name', 'members', 'created_at']
        read_only_fields = ['uuid', 'created_at']

class ChannelSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    
    class Meta:
        model = Channel
        fields = ['uuid', 'name', 'description', 'created_at', 'is_private', 'messages', 'groups']
        read_only_fields = ['uuid', 'created_at']
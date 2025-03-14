# backend\chat\models.py:

import uuid
from django.db import models
from user.models import User

class Channel(models.Model):
    """Канал для общения"""
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Group(models.Model):
    """Группа пользователей с доступом к каналу"""
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='groups')
    members = models.ManyToManyField(User, related_name='chat_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.channel.name})"

class Message(models.Model):
    """Сообщение в чате"""
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
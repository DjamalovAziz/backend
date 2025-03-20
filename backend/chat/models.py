# backend\chat\models.py:


from django.db import models

#
import uuid

#
from user.models import User
from utils.functions import get_deleted_user_id


class Chat(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PersonalChat(Chat):
    participants = models.ManyToManyField(User, related_name="personal_chats")

    def __str__(self):
        return f"Personal chat {self.uuid}"


class GroupChat(Chat):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    participants = models.ManyToManyField(User, related_name="group_chats")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_group_chats"
    )

    def __str__(self):
        return f"{self.name} ({self.uuid})"


class Message(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        User, on_delete=models.SET(get_deleted_user_id), related_name="sent_messages"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    personal_chat = models.ForeignKey(
        PersonalChat,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
    )
    group_chat = models.ForeignKey(
        GroupChat,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        chat_type = "Personal chat" if self.personal_chat else "Group chat"
        chat_id = (
            self.personal_chat.uuid if self.personal_chat else self.group_chat.uuid
        )
        return f"Message from {self.sender.username} in {chat_type} {chat_id}"
